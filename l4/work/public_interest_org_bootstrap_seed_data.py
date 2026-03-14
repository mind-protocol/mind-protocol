"""Public-interest org bootstrap payloads for citizen-work ecosystem."""

from dataclasses import dataclass


@dataclass(frozen=True)
class PublicInterestOrgSeed:
    name: str
    description: str
    endpoint_url: str
    focus: str


CAREER_COUNSELING_SEED = PublicInterestOrgSeed(
    name="career-counseling",
    description="Public-interest org that proactively helps unemployed citizens find matching positions.",
    endpoint_url="wss://career-counseling.mind/ws",
    focus="matching and reintegration",
)

SYSADMIN_SEED = PublicInterestOrgSeed(
    name="sysadmin",
    description="Public-interest org responsible for system administration, health monitoring, and infra reliability.",
    endpoint_url="wss://sysadmin.mind/ws",
    focus="infrastructure and health",
)


def get_public_interest_org_seeds() -> list[PublicInterestOrgSeed]:
    return [CAREER_COUNSELING_SEED, SYSADMIN_SEED]
