"""Tests for the KEYSTONE R1 revision code: groups, PC03 runner, analytic families, testbed seeds."""

from __future__ import annotations

from itertools import product
from math import comb
from pathlib import Path
import random
import sys
import warnings

import pytest

PROJECT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT / "scripts"))

from keystone.standard_groups import FFDHE2048, FFDHE3072, GROUPS  # noqa: E402
from keystone.threshold_kem import (  # noqa: E402
    combine_partial_decryptions,
    create_partial_decryption,
    dealer_keygen,
    open_record,
    seal_record,
    verify_partial_decryption,
)
import run_r1_analytic as analytic  # noqa: E402
import run_r1_pc03 as pc03  # noqa: E402
import run_r1_deadline_testbed as testbed  # noqa: E402

DESIGN = PROJECT.parent / "research-case/03-design/r1-reviewer-revision"


@pytest.mark.parametrize("group,pem", [(FFDHE2048, "ffdhe2048.pem"), (FFDHE3072, "ffdhe3072.pem")])
def test_standard_group_matches_openssl_export(group, pem):
    from cryptography.hazmat.primitives.serialization import load_pem_parameters

    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        numbers = load_pem_parameters((DESIGN / pem).read_bytes()).parameter_numbers()
    assert group.p == numbers.p
    assert group.q == (group.p - 1) // 2
    assert pow(group.g, group.q, group.p) == 1 and group.g != 1


def test_threshold_round_trip_on_ffdhe2048():
    rng = random.Random(7)
    group = GROUPS["ffdhe2048"]
    epoch = dealer_keygen(5, 3, ["d0", "d1", "d0", "d1", "d0"], group=group, randbelow=rng.randrange)
    sealed = seal_record(epoch.public_key, group, "r", b"payload", b"aad", randbelow=rng.randrange)
    partials = [create_partial_decryption(epoch.members[i], sealed.c1, group, b"ctx", randbelow=rng.randrange) for i in (1, 3, 5)]
    assert all(verify_partial_decryption(epoch.members[p.member_index], sealed.c1, p, group, b"ctx") for p in partials)
    assert open_record(epoch, sealed, partials, b"ctx") == b"payload"
    assert combine_partial_decryptions(partials, group) == combine_partial_decryptions(partials[::-1], group)
    tampered = partials[0].with_value((partials[0].value * group.g) % group.p)
    assert not verify_partial_decryption(epoch.members[1], sealed.c1, tampered, group, b"ctx")


def test_freeze_hash_is_recorded_and_checked():
    assert len(pc03.freeze_sha256()) == 64


def test_fixed_quota_sample_takes_two_per_domain():
    rng = random.Random(1)
    for _ in range(200):
        sample = pc03.fixed_quota_sample(32, 4, 8, rng)
        assert len(set(sample)) == 8
        assert sorted(m % 4 for m in sample) == [0, 0, 1, 1, 2, 2, 3, 3]


def test_prespecified_draw_count_meets_precision_targets():
    assert pc03.hoeffding_half_width(131072, 1.0) <= 0.005
    assert pc03.hoeffding_half_width(131072, 2.0) <= 0.010


def test_pc03_blocks_are_deterministic():
    cell = {"n": 32, "t": 22, "s": 8, "q": 8, "domains": 4, "independent_offline_probability": 0.1,
            "domain_outage_probability": 0.0}
    assert pc03.run_iid_block(cell, 123, 512) == pc03.run_iid_block(cell, 123, 512)


def test_selective_withholding_gap_is_total():
    cell = {"n": 32, "t": 22, "s": 8, "q": 8, "domains": 4, "independent_offline_probability": 0.0,
            "domain_outage_probability": 0.0, "selective_withholders": 11}
    counts = pc03.run_sw_block(cell, 5, 256)
    assert counts == {"audit_pass": 256, "dispute_success": 0, "gap_sum": 256}


@pytest.mark.parametrize("domains", [2, 4, 8])
@pytest.mark.parametrize("f", [0.1, 0.25])
def test_domain_exact_matches_enumeration(domains, f):
    size = 32 // domains
    recon = 0.0
    for state in product([0, 1], repeat=domains):
        weight = 1.0
        for down in state:
            weight *= f if down else 1 - f
        recon += weight * (size * state.count(0) >= 22)
    assert analytic.domain_exact(f, domains)[0] == pytest.approx(recon, abs=1e-12)


def test_hyper_tail_matches_static_bound_when_q_equals_s():
    assert analytic.hyper_tail(21, 32, 8, 8) == pytest.approx(comb(21, 8) / comb(32, 8), abs=1e-15)
    assert 1 - analytic.hyper_tail(21, 32, 8, 8) == pytest.approx(0.9806537178061093, abs=1e-12)


def test_iid_audit_pass_is_binomial_tail():
    assert analytic.iid_exact(0.1)[1] == pytest.approx(0.9**8, abs=1e-12)


def test_testbed_seeds_and_zero_delay_profile():
    assert testbed.trace_seed("D0-CONTROL", 0) == testbed.trace_seed("D0-CONTROL", 0)
    assert testbed.trace_seed("D0-CONTROL", 0) != testbed.trace_seed("D0-CONTROL", 1)
    assert testbed.one_way(random.Random(1), {"median_ms": 0, "sigma": 0}) == 0.0
    rng = random.Random(2)
    delays = sorted(testbed.one_way(rng, {"median_ms": 120, "sigma": 0.6}) for _ in range(4001))
    assert delays[2000] == pytest.approx(0.120, rel=0.08)
