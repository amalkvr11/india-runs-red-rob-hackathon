"""
rank.py — Redrob Hackathon CLI entry point.

Usage:
    python rank.py --candidates ./candidates.jsonl --out ./submission.csv [--top-k 100]

Matches the expected interface for the India Runs Data & AI Challenge:
    python rank.py --candidates <path> --out <path>
"""

import argparse
import logging
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from config import TOP_K
from ranker import rank_candidates


def main():
    parser = argparse.ArgumentParser(
        description="Redrob Hackathon — Candidate Ranking System"
    )
    parser.add_argument(
        "--candidates",
        required=True,
        help="Path to candidates.jsonl file",
    )
    parser.add_argument(
        "--out",
        required=True,
        help="Path for output submission.csv",
    )
    parser.add_argument(
        "--top-k",
        type=int,
        default=TOP_K,
        help=f"Number of top candidates (default: {TOP_K})",
    )

    args = parser.parse_args()

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s",
        datefmt="%H:%M:%S",
        stream=sys.stderr,
    )

    input_path = Path(args.candidates)
    if not input_path.exists():
        logging.error("Candidates file not found: %s", input_path.resolve())
        sys.exit(1)

    rank_candidates(
        candidates_path=str(input_path),
        output_path=args.out,
        top_k=args.top_k,
        verbose=False,
    )


if __name__ == "__main__":
    main()
