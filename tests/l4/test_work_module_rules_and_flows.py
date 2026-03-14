"""Tests for L4 work module implementation."""

import pytest

from l4.work import (
    PositionRegistration,
    create_position_nodes,
    requires_work,
    unemployment_decay_for_day,
    apply_unemployment_decay,
    evaluate_vacation_eligibility,
    ValueCascadeInputs,
    compute_value_cascade_delta,
    apply_human_partner_feedback,
    run_call_v1,
    CallOutcome,
    CandidateProfile,
    rank_candidates_for_position,
    spawn_basic_citizen_for_position,
    ValueCascadeTracker,
    WorkHealthSnapshot,
    build_work_health_report,
    get_public_interest_org_seeds,
)


def test_position_schema_creates_nodes_and_links():
    reg = PositionRegistration(
        org_id="org_123",
        title="Backend Builder",
        requirements="python graph matching",
        expectations="ship stable features",
        fill_count=2,
    )
    position_node, property_nodes, links, record = create_position_nodes(reg, position_id="position_test")

    assert position_node.type == "position"
    assert record.fill_count == 2
    assert len(property_nodes) == 4
    assert len(links) == 4


def test_work_requirement_and_vacation_rules():
    assert requires_work("lumina-prime") is True
    assert requires_work("contre-terre") is False

    assert unemployment_decay_for_day(3, on_vacation=False) == 0.0
    assert unemployment_decay_for_day(10, on_vacation=False) > 0.0
    assert unemployment_decay_for_day(45, on_vacation=False) > unemployment_decay_for_day(10, on_vacation=False)
    assert apply_unemployment_decay(1.0, days_unemployed=100, on_vacation=False) >= 0.0
    assert apply_unemployment_decay(50.0, days_unemployed=100, on_vacation=True) == 50.0

    decision = evaluate_vacation_eligibility(55)
    assert decision.eligible is True
    assert decision.available_days >= 1


def test_value_cascade_and_human_partner_signal():
    inputs = ValueCascadeInputs(
        scale=3.0,
        attention_count=4,
        usage_count=8,
        peer_validations=3,
        network_score=1.1,
    )
    delta = compute_value_cascade_delta(inputs)
    assert delta > 0

    improved = apply_human_partner_feedback(10.0, 0.5)
    reduced = apply_human_partner_feedback(10.0, -1.0)
    assert improved > 10.0
    assert reduced < 10.0


def test_call_v1_accept_and_timeout_paths():
    accepted = run_call_v1(
        caller_messages=["Hi, role proposal"],
        callee_messages=["yes, I accept"],
        max_turns=4,
    )
    assert accepted.outcome == CallOutcome.ACCEPTED

    timeout = run_call_v1(
        caller_messages=["proposal", "details"],
        callee_messages=["need more info", "still unsure"],
        max_turns=4,
    )
    assert timeout.outcome == CallOutcome.TIMEOUT


def test_matcher_spawner_tracker_health_and_org_bootstrap():
    ranked = rank_candidates_for_position(
        position_requirements="python graph matching",
        candidates=[
            CandidateProfile(
                citizen_id="citizen_a",
                status="active",
                capabilities_text="python graph matching",
                trust_score=80,
                active_memberships=1,
            ),
            CandidateProfile(
                citizen_id="citizen_b",
                status="active",
                capabilities_text="python",
                trust_score=90,
                active_memberships=0,
            ),
        ],
    )
    assert ranked
    assert ranked[0].citizen_id == "citizen_a"

    spawned = spawn_basic_citizen_for_position(
        position_id="position_x",
        org_id="org_y",
        requirements="python distributed graph ops",
    )
    assert spawned.origin_position_id == "position_x"
    assert spawned.trust_score == 0.0
    assert spawned.seeded_capabilities

    tracker = ValueCascadeTracker()
    tracker.record_event("citizen_a", "org_y", "artifact_1", 0.12)
    tracker.record_event("citizen_a", "org_y", "artifact_2", 0.08)
    assert tracker.trust_sum_for_citizen_org("citizen_a", "org_y") == pytest.approx(0.2)

    report = build_work_health_report(
        WorkHealthSnapshot(
            open_positions=2,
            filled_positions=8,
            timeout_calls=1,
            successful_calls=9,
            unemployed_lumina_prime=2,
            citizens_on_vacation=1,
        )
    )
    assert report.status in {"healthy", "warning", "critical"}
    assert 0 <= report.fill_rate <= 1

    seeds = get_public_interest_org_seeds()
    assert {seed.name for seed in seeds} == {"career-counseling", "sysadmin"}
