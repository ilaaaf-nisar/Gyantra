# GYANTRA

**Your Private AI Learning Companion**

GYANTRA is a Windows desktop study assistant built around a small, locally
running language model. It is intended to help learners explore topics found in
IGNOU MCA and M.Sc. course materials, ask follow-up questions, and get concise
explanations without sending chat prompts to a hosted AI service.

The project brings together a desktop chat interface, a local Python inference
server, a custom decoder-only transformer, reviewed question-and-answer
examples, and scripts for preparing course text and training model checkpoints.
It is also an educational project: its model and training workflow are small
enough to inspect, but its answers are not a substitute for course materials.

## What GYANTRA does

- Opens a chat UI in a native desktop window.
- Runs the UI's inference API on this computer at `127.0.0.1:8000`.
- Checks a local set of reviewed Q&A examples first. Exact matches and
  conservative keyword-overlap matches can return those answers directly.
- Uses the local transformer to generate an answer when no reviewed answer
  matches.
- Includes recent turns in follow-up prompts and offers controls for response
  length, temperature, and top-k sampling.
- Uses CUDA or Apple MPS for inference when available, and otherwise can run
  inference on CPU.

**GYANTRA does not currently search or retrieve passages from PDFs when you ask
a question.** The course corpus is used by the training workflow; the chat
server does not look up source passages at response time. The reviewed Q&A
lookup is not a document-retrieval system, and generated answers may be
incorrect or incomplete.

## Architecture

```text
Start GYANTRA.bat
       |
       v
app.py -- starts chat_server.py's handler in a background thread
       |                                      |
       v                                      v
pywebview opens the local HTML UI      127.0.0.1:8000/generate
       |                                      |
       +---- POST prompt, settings, history ->|
                                              v
                                  Validate request and check
                                  reviewed Q&A (qa_lookup.py)
                                      |               |
                              reviewed match      no match
                                      |               |
                                      |      GPT-2 BPE tokenization
                                      |      + DecoderLLM generation
                                      +---------------+
                                              |
                                      JSON completion
                                              |
                                              v
                                      Chat interface
```

### Chat and inference

1. `Start GYANTRA.bat` checks that the project's `.venv` and `pywebview`
   installation are available, then launches `app.py`.
2. `app.py` switches to the project directory, loads `chat_server.py`, starts
   its threaded HTTP server, and opens `ignou_llm_web_interface.html` in a
   pywebview desktop window.
3. The interface sends a JSON `POST` to `/generate` with the prompt, up to four
   recent conversation turns, and generation settings.
4. `chat_server.py` validates the request. `qa_lookup.py` first looks for a
   reviewed response using normalized text and a conservative weighted
   word-overlap match. If it finds none, the server tokenizes the conversation,
   calls the model, and returns the generated text as JSON.
5. Closing the desktop window shuts down the local server.

The server binds to loopback (`127.0.0.1`), not to a public network interface.
Inference does not call a hosted AI API. Internet access may still be needed to
install dependencies, download tokenizer data on first use, or use the optional
course-download mode described below.

### Model

`model.py` implements a decoder-only transformer with causal self-attention,
feed-forward blocks, token and position embeddings, and an autoregressive
sampling loop. The configured model has:

- GPT-2 BPE tokenization through `tiktoken`
- 4 transformer layers
- 4 attention heads
- 256 embedding dimensions
- A configured context window of 512 tokens

The context window applies to the model's input sequence; it is not the maximum
answer length. Generation repeatedly uses the most recent context window.
Because this is a small custom model trained on limited data, it is not
comparable to a large hosted model.

## Run the desktop app

The normal launch path is Windows and expects the project virtual environment
and fine-tuned checkpoint to be present.

1. From the project folder, create or activate a Python virtual environment if
   needed:

   ```powershell
   python -m venv .venv
   .\.venv\Scripts\python.exe -m pip install -r requirements.txt
   ```

2. Make sure `checkpoints/ignou_llm_sft.pt` and
   `data/instructions.json` are present. The server loads both at startup.
3. Double-click `Start GYANTRA.bat`, or run:

   ```powershell
   .\.venv\Scripts\python.exe .\app.py
   ```

4. If the desktop window cannot open, install or repair the Microsoft Edge
   WebView2 Runtime.

The batch launcher uses the existing `.venv`; if `pywebview` is missing, it
installs the packages in `requirements.txt`. Starting the server directly for
troubleshooting is also possible:

```powershell
.\.venv\Scripts\python.exe .\chat_server.py
```

The server listens at `http://127.0.0.1:8000/generate`. It requires the
fine-tuned checkpoint and reviewed-answer JSON file; it is not a standalone
replacement for the desktop launcher.

## Prepare data and train

Training is optional for everyday app use. It rebuilds local artifacts and can
take a long time. Run commands from the project directory.

### Requirements for the training workflow

`requirements.txt` lists the app's direct dependencies: PyTorch, `tiktoken`,
and `pywebview`. The preparation and tokenization scripts also import packages
that are not listed there. Install them when running that workflow:

```powershell
.\.venv\Scripts\python.exe -m pip install numpy pymupdf beautifulsoup4 requests urllib3
```

`train.py` requires a supported GPU (CUDA or Apple MPS); it deliberately stops
instead of silently training on CPU. `finetune.py` can use CUDA, MPS, or CPU.

### Full pipeline

The pipeline runs these stages in order and stops if a stage fails:

```powershell
.\.venv\Scripts\python.exe .\pipeline.py
```

By default, it extracts PDFs already stored under `data/courses`. To download
MCA PDFs from eGyanKosh before extraction, use:

```powershell
.\.venv\Scripts\python.exe .\pipeline.py --crawl
```

The crawl option requires internet access. Review the source site's terms and
the downloaded material's usage rights before distributing course files or
derived datasets.

The stages are:

1. **Extract course text — `data_prep.py`:** reads local PDFs below
   `data/courses` and writes `data/corpus.txt`. With `--crawl`, it first
   downloads selected MCA block PDFs for semesters I–IV.
2. **Tokenize — `tokeniser.py`:** encodes the corpus with the GPT-2 tokenizer,
   makes a 90/10 train/validation split, and writes `data/train.bin` and
   `data/val.bin`.
3. **Create Q&A JSON — `generate_dataset.py`:** requires that `data/corpus.txt`
   exists, then writes the reviewed examples defined in that script to
   `data/instructions.json`. It does not automatically extract questions and
   answers from the corpus.
4. **Pretrain — `train.py`:** trains the base model on the binary corpus split
   and saves `checkpoints/ignou_llm_final.pt`.
5. **Fine-tune — `finetune.py`:** trains on valid prompt/response pairs from
   `data/instructions.json` and saves
   `checkpoints/ignou_llm_sft.pt`, the checkpoint loaded by the app.

The pipeline regenerates data files and overwrites both checkpoints. Back up
any artifacts you need before retraining. The fine-tuning script expects at
least 20 valid Q&A examples.

### Run individual stages

```powershell
# Add course PDFs under data/courses first.
.\.venv\Scripts\python.exe .\data_prep.py
.\.venv\Scripts\python.exe .\tokeniser.py
.\.venv\Scripts\python.exe .\generate_dataset.py
.\.venv\Scripts\python.exe .\train.py
.\.venv\Scripts\python.exe .\finetune.py
```

`prepare_sft.py` is a separate utility that creates `data/sft_train.bin`.
Despite its name, the current `finetune.py` reads `data/instructions.json`
directly, so that binary file is not part of the current pipeline.

## Tests

Run the reviewed-answer matching tests from the project directory:

```powershell
.\.venv\Scripts\python.exe -m unittest discover -s tests
```

## Repository structure

```text
GYANTRA/
├── app.py                         # Desktop-window and local-server lifecycle
├── chat_server.py                 # Local /generate HTTP API and model inference
├── model.py                       # Decoder-only transformer implementation
├── qa_lookup.py                   # Reviewed Q&A matching
├── ignou_llm_web_interface.html   # Chat UI (HTML, CSS, and JavaScript)
├── Start GYANTRA.bat              # Windows launcher
├── requirements.txt               # App runtime dependencies
├── pipeline.py                    # Ordered data-preparation/training runner
├── data_prep.py                   # PDF crawling (optional) and text extraction
├── tokeniser.py                   # GPT-2 encoding and train/validation split
├── generate_dataset.py            # Reviewed prompt/response source data
├── train.py                       # Base-model pretraining
├── finetune.py                    # Supervised fine-tuning
├── prepare_sft.py                 # Optional/legacy SFT binary preparation
├── tests/
│   └── test_qa_lookup.py           # Reviewed-answer matcher tests
├── data/
│   ├── courses/                   # Input PDFs for data preparation
│   ├── corpus.txt                 # Extracted course text
│   ├── instructions.json          # Reviewed prompt/response examples
│   ├── train.bin                  # Tokenized pretraining split
│   ├── val.bin                    # Tokenized validation split
│   └── sft_train.bin              # Optional output from prepare_sft.py
└── checkpoints/
    ├── ignou_llm_final.pt         # Base pretrained model
    └── ignou_llm_sft.pt           # Fine-tuned model used by the app
```

The `data/` and `checkpoints/` files are data/model artifacts rather than
application source. Their presence can depend on how the project was obtained;
the desktop app specifically needs `data/instructions.json` and
`checkpoints/ignou_llm_sft.pt`. The `.venv/` directory, if present, is a local
Python environment and should be recreated for another machine rather than
treated as source code.

## Limitations

- A generated answer can be inaccurate; verify important details against the
  official course materials.
- The app does not cite or retrieve passages from local PDFs at answer time.
- The model is small and trained from limited data; it may produce irrelevant
  text, repeat itself, or fail on questions outside its examples and training.
- Inference may be slow on CPU. Base-model pretraining requires supported GPU
  hardware.
- The data preparation workflow's optional crawler requires an internet
  connection; local inference itself does not require a cloud model or API key.
