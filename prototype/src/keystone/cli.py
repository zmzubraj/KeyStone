from __future__ import annotations

import argparse
import json
import random
from pathlib import Path

from .protocol import CustodianBehavior, derive_canary, execute_audit, execute_dispute
from .sampling import catastrophic_false_accept_probability
from .simulation import Scenario, run_monte_carlo
from .threshold_kem import dealer_keygen, seal_record


def _demo() -> int:
    rng = random.Random(20260829)
    domains = ["aws-eu"] * 3 + ["gcp-us"] * 3 + ["azure-ap"] * 2 + ["independent"] * 2
    epoch = dealer_keygen(10, 7, domains, epoch_id="demo-epoch", randbelow=rng.randrange)
    sealed = seal_record(
        epoch.public_key,
        epoch.group,
        "demo-record",
        b"encrypted AI inference receipt",
        b"keystone-demo",
    )
    behaviors = {index: CustodianBehavior(latency_ms=25 + index) for index in epoch.members}
    canary = derive_canary(epoch, b"demo-finalized-beacon", b"demo-audit")
    audit = execute_audit(
        epoch,
        canary,
        sampled_indices=[1, 3, 5, 7, 9],
        behaviors=behaviors,
        deadline_ms=100,
        required_valid=5,
        context=b"demo-audit",
    )
    dispute = execute_dispute(
        epoch,
        sealed,
        behaviors,
        deadline_ms=100,
        context=b"demo-dispute",
    )
    print(json.dumps({
        "audit_passed": audit.passed,
        "audit_valid_responses": audit.valid_responses,
        "dispute_success": dispute.success,
        "plaintext": dispute.plaintext.decode() if dispute.plaintext else None,
    }, indent=2))
    return 0 if audit.passed and dispute.success else 1


def _bound(args: argparse.Namespace) -> int:
    probability = catastrophic_false_accept_probability(
        args.n,
        args.threshold,
        args.sample_size,
        args.required_valid,
    )
    print(json.dumps({
        "false_accept_probability": probability,
        "detection_probability": 1.0 - probability,
    }, indent=2))
    return 0


def _simulate(args: argparse.Namespace) -> int:
    raw = json.loads(Path(args.config).read_text(encoding="utf-8"))
    scenarios = raw if isinstance(raw, list) else [raw]
    results = [run_monte_carlo(Scenario(**scenario)) for scenario in scenarios]
    output = json.dumps(results, indent=2)
    if args.output:
        Path(args.output).write_text(output + "\n", encoding="utf-8")
    print(output)
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="KEYSTONE research prototype")
    subparsers = parser.add_subparsers(dest="command", required=True)

    subparsers.add_parser("demo", help="run an end-to-end cryptographic demo")

    bound = subparsers.add_parser("bound", help="calculate the catastrophic false-accept bound")
    bound.add_argument("--n", type=int, required=True)
    bound.add_argument("--threshold", type=int, required=True)
    bound.add_argument("--sample-size", type=int, required=True)
    bound.add_argument("--required-valid", type=int)

    simulate = subparsers.add_parser("simulate", help="run JSON-defined Monte Carlo scenarios")
    simulate.add_argument("--config", required=True)
    simulate.add_argument("--output")
    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    if args.command == "demo":
        return _demo()
    if args.command == "bound":
        return _bound(args)
    if args.command == "simulate":
        return _simulate(args)
    parser.error("unknown command")
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
