import argparse
import subprocess
import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parent
PIPELINE_STEPS = (
    ("Extracting local course PDFs", "data_prep.py"),
    ("Tokenizing the course corpus", "tokeniser.py"),
    ("Generating reviewed Q&A examples", "generate_dataset.py"),
    ("Pretraining the base model", "train.py"),
    ("Fine-tuning on reviewed examples", "finetune.py"),
)


def main():
    parser = argparse.ArgumentParser(
        description="Run the complete GYANTRA data preparation and training pipeline."
    )
    parser.add_argument(
        "--crawl",
        action="store_true",
        help="Download MCA PDFs before extraction (requires internet).",
    )
    args = parser.parse_args()

    for label, script_name in PIPELINE_STEPS:
        command = [sys.executable, "-u", str(PROJECT_ROOT / script_name)]
        if args.crawl and script_name == "data_prep.py":
            command.append("--crawl")

        print(f"\n=== {label} ===", flush=True)
        try:
            subprocess.run(command, cwd=PROJECT_ROOT, check=True)
        except subprocess.CalledProcessError as error:
            print(
                f"\nPipeline stopped: {script_name} exited with "
                f"status {error.returncode}.",
                file=sys.stderr,
                flush=True,
            )
            return error.returncode or 1
        except KeyboardInterrupt:
            print("\nPipeline interrupted.", file=sys.stderr, flush=True)
            return 130

    print("\nGYANTRA pipeline completed successfully.", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
