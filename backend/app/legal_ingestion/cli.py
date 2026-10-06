"""Run with: python -m app.legal_ingestion.cli --dry-run <public files>."""
import argparse
import json
from .service import dry_run


def main(argv=None):
    parser = argparse.ArgumentParser(description="Inspect Legal Knowledge V2 structure offline")
    parser.add_argument("paths", nargs="+", help="Local public legal source files")
    parser.add_argument("--dry-run", action="store_true", required=True)
    parser.add_argument("--family", choices=("auto", "normative", "jurisprudence"), default="auto")
    parser.add_argument("--max-unit-tokens", type=int, default=800)
    args = parser.parse_args(argv)
    summary = dry_run(args.paths, family=args.family, max_unit_tokens=args.max_unit_tokens)
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
