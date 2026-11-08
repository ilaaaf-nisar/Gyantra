import json
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

import torch
import tiktoken

from model import DEFAULT_BLOCK_SIZE, DecoderLLM
from qa_lookup import find_reviewed_answer, load_reviewed_answers


HOST = "127.0.0.1"
PORT = 8000
CHECKPOINT_PATH = Path("checkpoints/ignou_llm_sft.pt")
BLOCK_SIZE = DEFAULT_BLOCK_SIZE
MAX_REQUEST_BYTES = 1_000_000

device = torch.device(
    "cuda" if torch.cuda.is_available()
    else "mps" if torch.backends.mps.is_available()
    else "cpu"
)
enc = tiktoken.get_encoding("gpt2")
reviewed_answers = load_reviewed_answers()

if not CHECKPOINT_PATH.is_file():
    raise FileNotFoundError(
        f"Fine-tuned checkpoint not found: {CHECKPOINT_PATH}. "
        "Run prepare_sft.py and finetune.py first."
    )

checkpoint = torch.load(CHECKPOINT_PATH, map_location=device)
checkpoint_block_size = checkpoint["position_embedding.weight"].shape[0]
if checkpoint_block_size != BLOCK_SIZE:
    print(
        f"Warning: checkpoint context is {checkpoint_block_size} tokens; "
        f"the configured training context is {BLOCK_SIZE}. Retrain with "
        "'.\\.venv\\Scripts\\python.exe .\\train.py' and then "
        "'.\\.venv\\Scripts\\python.exe .\\finetune.py' to use the larger context."
    )
model = DecoderLLM(
    vocab_size=enc.n_vocab,
    n_embd=256,
    n_head=4,
    n_layer=4,
    block_size=checkpoint_block_size,
).to(device)
model.load_state_dict(checkpoint)
model.eval()
generation_lock = threading.Lock()

print(f"Loaded {CHECKPOINT_PATH} on {device} with a {checkpoint_block_size}-token context")


class ChatHandler(BaseHTTPRequestHandler):
    def _send_json(self, status, payload):
        body = json.dumps(payload).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()
        self.wfile.write(body)

    def do_OPTIONS(self):
        self._send_json(200, {})

    def do_POST(self):
        if self.path != "/generate":
            self._send_json(404, {"error": "Endpoint not found"})
            return

        try:
            content_length = int(self.headers.get("Content-Length", "0"))
            if content_length <= 0 or content_length > MAX_REQUEST_BYTES:
                self._send_json(413, {"error": "Request body is empty or too large"})
                return

            request = json.loads(self.rfile.read(content_length))
            if not isinstance(request, dict):
                self._send_json(400, {"error": "Request body must be a JSON object"})
                return

            prompt = request.get("prompt")
            if not isinstance(prompt, str) or not prompt.strip():
                self._send_json(400, {"error": "A non-empty prompt is required"})
                return

            history = request.get("history", [])
            if not isinstance(history, list) or len(history) > 20:
                self._send_json(400, {"error": "history must be a list of at most 20 turns"})
                return

            validated_history = []
            for turn in history:
                if (
                    not isinstance(turn, dict)
                    or not isinstance(turn.get("user"), str)
                    or not isinstance(turn.get("assistant"), str)
                    or len(turn["user"]) > 20_000
                    or len(turn["assistant"]) > 20_000
                ):
                    self._send_json(
                        400,
                        {"error": "Each history turn must contain user and assistant text under 20000 characters"},
                    )
                    return
                validated_history.append(turn)

            max_new_tokens = request.get("max_new_tokens", 60)
            temperature = request.get("temperature", 0.8)
            top_k = request.get("top_k", 40)
            if (
                isinstance(max_new_tokens, bool)
                or not isinstance(max_new_tokens, int)
                or not 1 <= max_new_tokens <= 3000
            ):
                self._send_json(400, {"error": "max_new_tokens must be between 1 and 3000"})
                return
            if (
                isinstance(temperature, bool)
                or not isinstance(temperature, (int, float))
                or not 0 < temperature <= 1.5
            ):
                self._send_json(400, {"error": "temperature must be greater than 0 and at most 1.5"})
                return
            if (
                isinstance(top_k, bool)
                or not isinstance(top_k, int)
                or not 1 <= top_k <= enc.n_vocab
            ):
                self._send_json(400, {"error": f"top_k must be between 1 and {enc.n_vocab}"})
                return

            reviewed_answer = find_reviewed_answer(prompt, reviewed_answers)
            if reviewed_answer is not None:
                answer_tokens = enc.encode_ordinary(reviewed_answer)[:max_new_tokens]
                self._send_json(
                    200,
                    {
                        "completion": enc.decode(answer_tokens),
                        "tokens": len(answer_tokens),
                        "source": "reviewed_example",
                    },
                )
                return

            chat_prompt = "".join(
                f"<|user|> {turn['user'].strip()}\n"
                f"<|assistant|> {turn['assistant'].strip()}\n"
                for turn in validated_history
            )
            chat_prompt += f"<|user|> {prompt.strip()}\n<|assistant|>"
            tokens = enc.encode_ordinary(chat_prompt)[-BLOCK_SIZE:]
            context = torch.tensor([tokens], dtype=torch.long, device=device)

            with generation_lock, torch.no_grad():
                output = model.generate(
                    context,
                    max_new_tokens=max_new_tokens,
                    temperature=float(temperature),
                    top_k=top_k,
                )

            full_output = enc.decode(output[0].tolist())
            if "<|assistant|>" in full_output:
                reply = full_output.split("<|assistant|>")[-1]
                reply = reply.split("<|endoftext|>")[0].split("<|user|>")[0].strip()
            else:
                reply = full_output

            self._send_json(
                200,
                {
                    "completion": reply,
                    "tokens": max(0, output.shape[1] - len(tokens)),
                    "source": "model",
                },
            )
        except (json.JSONDecodeError, UnicodeDecodeError, ValueError) as error:
            self._send_json(400, {"error": f"Invalid request: {error}"})
        except Exception as error:
            print(f"Generation failed: {error}")
            self._send_json(500, {"error": "Model generation failed"})

    def log_message(self, format, *args):
        print(f"{self.address_string()} - {format % args}")


if __name__ == "__main__":
    server = ThreadingHTTPServer((HOST, PORT), ChatHandler)
    print(f"IGNOU chat API listening at http://{HOST}:{PORT}/generate")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nStopping chat API...")
    finally:
        server.server_close()
