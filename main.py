import argparse
import logging
import sys
from pathlib import Path

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))

from config import TOP_K
from ranker import rank_candidates


def setup_logging(verbose: bool):
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format="%(asctime)s [%(levelname)s] %(message)s",
        datefmt="%H:%M:%S",
        stream=sys.stderr,
    )


def main():
    parser = argparse.ArgumentParser(
        description="Redrob Hackathon — Candidate Ranker"
    )
    parser.add_argument(
        "--input", "-i",
        default=r"[PUB] India_runs_data_and_ai_challenge\India_runs_data_and_ai_challenge\candidates.jsonl",
        help="Path to candidates.jsonl (default: the challenge data file)",
    )
    parser.add_argument(
        "--output", "-o",
        default="submission.csv",
        help="Output CSV path (default: submission.csv)",
    )
    parser.add_argument(
        "--top-k", type=int, default=TOP_K,
        help=f"Number of top candidates to output (default: {TOP_K})",
    )
    parser.add_argument(
        "--verbose", "-v", action="store_true",
        help="Enable verbose debug logging",
    )

    args = parser.parse_args()

    setup_logging(args.verbose)
    logger = logging.getLogger(__name__)

    input_path = Path(args.input)
    if not input_path.exists():
        logger.error("Input file not found: %s", input_path.resolve())
        sys.exit(1)

    rank_candidates(
        candidates_path=str(input_path),
        output_path=args.output,
        top_k=args.top_k,
        verbose=args.verbose,
    )


if __name__ == "__main__":
    main()
