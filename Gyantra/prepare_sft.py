
import json
import os
import re
import numpy as np
import tiktoken


SOURCE_MARKER = re.compile(r"===\s*SOURCE\s*:", re.IGNORECASE)


def create_sft_dataset(input_json="data/instructions.json", output_bin="data/sft_train.bin"):
    enc = tiktoken.get_encoding("gpt2")
    
    if not os.path.exists(input_json):
        raise FileNotFoundError(f"Missing {input_json}")

    with open(input_json, "r", encoding="utf-8") as f:
        pairs = json.load(f)

    if not isinstance(pairs, list):
        raise ValueError(f"{input_json} must contain a JSON list of prompt/response pairs.")

    formatted_texts = []
    for item in pairs:
        if not isinstance(item, dict):
            continue
        prompt = item.get("prompt")
        response = item.get("response")
        if not isinstance(prompt, str) or not isinstance(response, str):
            continue
        prompt = prompt.strip()
        response = response.strip()
        if not prompt or not response or SOURCE_MARKER.search(response):
            continue
        dialogue = f"<|user|> {prompt}\n<|assistant|> {response}<|endoftext|>\n"
        formatted_texts.append(dialogue)

    if not formatted_texts:
        raise ValueError(f"No valid prompt/response examples found in {input_json}.")

    full_text = "".join(formatted_texts)
    tokens = enc.encode_ordinary(full_text)
    
    print(f"Using {len(formatted_texts)} valid examples; total conversational tokens: {len(tokens)}")

    token_array = np.array(tokens, dtype=np.uint16)
    token_array.tofile(output_bin)
    print(f"Saved SFT dataset to {output_bin}")

if __name__ == "__main__":
    create_sft_dataset()