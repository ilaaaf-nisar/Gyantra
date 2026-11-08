import json
import os
import re

import tiktoken
import torch
from model import DEFAULT_BLOCK_SIZE, DecoderLLM


DEVICE = torch.device(
    "cuda" if torch.cuda.is_available()
    else "mps" if torch.backends.mps.is_available()
    else "cpu"
)
BLOCK_SIZE = DEFAULT_BLOCK_SIZE
BATCH_SIZE = 2
TRAIN_STEPS = 600
SOURCE_MARKER = re.compile(r"===\s*SOURCE\s*:", re.IGNORECASE)

print(f"Fine-tuning on device: {DEVICE}")

enc = tiktoken.get_encoding("gpt2")
instructions_path = "data/instructions.json"
if not os.path.isfile(instructions_path):
    raise FileNotFoundError(
        f"Missing {instructions_path}. Run generate_dataset.py first."
    )

with open(instructions_path, "r", encoding="utf-8") as instructions_file:
    examples = json.load(instructions_file)
if not isinstance(examples, list):
    raise ValueError(f"{instructions_path} must contain a JSON list.")

eos_tokens = enc.encode_ordinary("<|endoftext|>")
padding_token = enc.eot_token
training_examples = []
for item in examples:
    if not isinstance(item, dict):
        continue
    prompt = item.get("prompt")
    response = item.get("response")
    if (
        not isinstance(prompt, str)
        or not isinstance(response, str)
        or not prompt.strip()
        or not response.strip()
        or SOURCE_MARKER.search(response)
    ):
        continue

    prefix = f"<|user|> {prompt.strip()}\n<|assistant|>"
    dialogue = f"{prefix}{response.strip()}<|endoftext|>"
    tokens = enc.encode_ordinary(dialogue)
    prefix_tokens = enc.encode_ordinary(prefix)
    prefix_length = 0
    for prefix_token, dialogue_token in zip(prefix_tokens, tokens):
        if prefix_token != dialogue_token:
            break
        prefix_length += 1

    if prefix_length >= BLOCK_SIZE:
        raise ValueError(f"Prompt is too long for the training context: {prompt}")

    max_length = BLOCK_SIZE + 1
    if len(tokens) > max_length:
        tokens = tokens[: max_length - len(eos_tokens)] + eos_tokens

    input_tokens = tokens[:-1]
    target_tokens = tokens[1:]
    targets = [-100 if index + 1 < prefix_length else token
               for index, token in enumerate(target_tokens)]

    padding = BLOCK_SIZE - len(input_tokens)
    input_tokens.extend([padding_token] * padding)
    targets.extend([-100] * padding)
    training_examples.append((
        torch.tensor(input_tokens, dtype=torch.long),
        torch.tensor(targets, dtype=torch.long),
    ))

if len(training_examples) < 20:
    raise ValueError(
        f"Only {len(training_examples)} valid Q&A examples found. "
        "Add at least 20 reviewed examples before fine-tuning."
    )
print(f"Using {len(training_examples)} reviewed Q&A examples.")

model = DecoderLLM(
    vocab_size=enc.n_vocab,
    n_embd=256,
    n_head=4,
    n_layer=4,
    block_size=BLOCK_SIZE,
).to(DEVICE)

base_checkpoint = "checkpoints/ignou_llm_final.pt"
if not os.path.isfile(base_checkpoint):
    raise FileNotFoundError(f"Base model checkpoint not found: {base_checkpoint}")
model.load_state_dict(torch.load(base_checkpoint, map_location=DEVICE))
print(f"Loaded base model weights from {base_checkpoint}")

optimizer = torch.optim.AdamW(model.parameters(), lr=5e-5)
print("Starting supervised fine-tuning on assistant responses...")
model.train()
for step in range(TRAIN_STEPS):
    indices = torch.randint(len(training_examples), (BATCH_SIZE,)).tolist()
    xb = torch.stack([training_examples[index][0] for index in indices]).to(DEVICE)
    yb = torch.stack([training_examples[index][1] for index in indices]).to(DEVICE)
    _, loss = model(xb, yb)

    optimizer.zero_grad(set_to_none=True)
    loss.backward()
    optimizer.step()

    if step % 100 == 0 or step == TRAIN_STEPS - 1:
        print(f"SFT Step {step:3d} | Assistant loss: {loss.item():.4f}")

model.eval()
sft_checkpoint = "checkpoints/ignou_llm_sft.pt"
torch.save(model.state_dict(), sft_checkpoint)
print(f"Fine-tuned model saved to {sft_checkpoint}")
