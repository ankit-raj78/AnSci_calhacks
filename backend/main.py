from io import BytesIO
import argparse
from ansci.workflow import create_animation


def main(paper_path: str, output_path: str, prompt: str | None = None):
    with open(paper_path, "rb") as paper_file:
        paper_bytes = BytesIO(paper_file.read())
        create_animation(paper_bytes, output_path, prompt)
    print(f"Hello from server! {paper_path} {output_path}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--paper", type=str, required=True)
    parser.add_argument("--output", type=str, required=True)
    parser.add_argument("--prompt", type=str)
    args = parser.parse_args()
    main(args.paper, args.output, args.prompt)
