#!/usr/bin/env python3
"""Run the deterministic Capability Gateway v1 no-effect reference provider."""

from __future__ import annotations

import argparse
import importlib.util
import json
from pathlib import Path
import sys


def load_contract_module():
    module_path = Path(__file__).resolve().parents[1] / "conformance" / "capability_gateway_v1.py"
    spec = importlib.util.spec_from_file_location("dubnium_capability_gateway_v1", module_path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load conformance module: {module_path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("request", type=Path)
    parser.add_argument("manifest", type=Path)
    args = parser.parse_args()
    contract = load_contract_module()
    try:
        result = contract.execute_no_effect(
            contract.load_json(args.request),
            contract.load_json(args.manifest),
        )
    except contract.ContractError as caught:
        print(json.dumps({"error": caught.envelope()}, sort_keys=True), file=sys.stderr)
        return 1
    print(json.dumps(result, ensure_ascii=False, sort_keys=True, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
