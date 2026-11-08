# tokenizer.py
import os
import numpy as np
import tiktoken

def process_corpus(input_path="data/corpus.txt", output_dir="data"):
    # 1. Choose or train your tokenizer (GPT-2 BPE via tiktoken)
    enc = tiktoken.get_encoding("gpt2")
    
    with open(input_path, "r", encoding="utf-8") as f:
        data = f.read()

    # 2. Encode full text to token IDs
    tokens = enc.encode_ordinary(data)
    print(f"Total tokens in corpus: {len(tokens):,}")

    # 3. Train / Validation split (90% / 10%)
    n = int(0.9 * len(tokens))
    train_tokens = tokens[:n]
    val_tokens = tokens[n:]

    # 4. Save as raw binary numpy arrays (uint16 covers vocab < 65,536; GPT-2 vocab is 50,257)
    train_ids = np.array(train_tokens, dtype=np.uint16)
    val_ids = np.array(val_tokens, dtype=np.uint16)

    train_ids.tofile(os.path.join(output_dir, "train.bin"))
    val_ids.tofile(os.path.join(output_dir, "val.bin"))
    print("Saved train.bin and val.bin to", output_dir)

if __name__ == "__main__":
    process_corpus()