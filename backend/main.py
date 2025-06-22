import argparse


def main(paper_path: str, output_path: str):
    print(f"Hello from server! {paper_path} {output_path}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--paper", type=str, required=True)
    parser.add_argument("--output", type=str, required=True)
    parser.add_argument("--prompt", type=str, required=True)
    args = parser.parse_args()
    main(args.paper, args.output)
