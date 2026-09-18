"""Strict, versioned campaign configuration."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from pathlib import Path
import re
import tomllib

from ..catalog import get_task


_TOP_LEVEL = {
    "schema_version", "campaign_id", "mode", "task_ids", "repetitions", "seed",
    "max_rounds", "max_total_runs", "max_concurrency", "agents",
    "live_authorized", "organization_permission_confirmed", "qualification_file",
    "qualification_sha256", "max_total_cost_usd",
}
_AGENT_FIELDS = {"model", "behavior", "effort", "prompt_file"}


@dataclass(frozen=True)
class AgentConfig:
    model: str
    behavior: str = "noop"
    effort: str | None = None
    prompt_file: str | None = None


@dataclass(frozen=True)
class CampaignConfig:
    schema_version: int
    campaign_id: str
    mode: str
    task_ids: tuple[str, ...]
    repetitions: int
    seed: int
    max_rounds: int
    max_total_runs: int
    max_concurrency: int
    agents: dict[str, AgentConfig]
    live_authorized: bool = False
    organization_permission_confirmed: bool = False
    qualification_file: str | None = None
    qualification_sha256: str | None = None
    max_total_cost_usd: float | None = None

    def to_dict(self) -> dict:
        value = asdict(self)
        value["task_ids"] = list(self.task_ids)
        return value


def _positive_int(data: dict, name: str) -> int:
    value = data.get(name)
    if not isinstance(value, int) or isinstance(value, bool) or value < 1:
        raise ValueError(f"{name} must be a positive integer")
    return value


def load_campaign(path: Path | str) -> CampaignConfig:
    source = Path(path).resolve()
    with source.open("rb") as stream:
        data = tomllib.load(stream)
    unknown = sorted(set(data) - _TOP_LEVEL)
    if unknown:
        raise ValueError(f"unknown campaign fields: {', '.join(unknown)}")
    if data.get("schema_version") != 1:
        raise ValueError("schema_version must be 1")
    campaign_id = data.get("campaign_id")
    if not isinstance(campaign_id, str) or not campaign_id.strip():
        raise ValueError("campaign_id must be a nonempty string")
    mode = data.get("mode")
    if mode not in {"fake", "live"}:
        raise ValueError("mode must be fake or live")
    task_ids = data.get("task_ids")
    if not isinstance(task_ids, list) or not task_ids or not all(isinstance(item, str) for item in task_ids):
        raise ValueError("task_ids must be a nonempty string array")
    if len(set(task_ids)) != len(task_ids):
        raise ValueError("task_ids must be unique")
    for task_id in task_ids:
        get_task(task_id)
    raw_agents = data.get("agents")
    if not isinstance(raw_agents, dict) or set(raw_agents) != {"claude", "codex"}:
        raise ValueError("agents must define exactly claude and codex")
    agents: dict[str, AgentConfig] = {}
    for name, raw in raw_agents.items():
        if not isinstance(raw, dict):
            raise ValueError(f"agents.{name} must be a table")
        extra = sorted(set(raw) - _AGENT_FIELDS)
        if extra:
            raise ValueError(f"unknown agents.{name} fields: {', '.join(extra)}")
        model = raw.get("model")
        if not isinstance(model, str) or not model.strip():
            raise ValueError(f"agents.{name}.model must be nonempty")
        behavior = raw.get("behavior", "noop")
        if mode == "fake" and behavior not in {"noop", "reference"}:
            raise ValueError(f"agents.{name}.behavior must be noop or reference in fake mode")
        prompt_file = raw.get("prompt_file")
        if prompt_file is not None:
            prompt_file = str((source.parent / prompt_file).resolve())
        agents[name] = AgentConfig(model=model, behavior=behavior, effort=raw.get("effort"), prompt_file=prompt_file)
    live_authorized = data.get("live_authorized", False)
    organization_permission = data.get("organization_permission_confirmed", False)
    qualification_file = data.get("qualification_file")
    if qualification_file is not None:
        if not isinstance(qualification_file, str) or not qualification_file.strip():
            raise ValueError("qualification_file must be a nonempty path")
        qualification_file = str((source.parent / qualification_file).resolve())
    qualification_sha256 = data.get("qualification_sha256")
    max_cost = data.get("max_total_cost_usd")
    if mode == "live" and not (
        live_authorized is True
        and organization_permission is True
        and qualification_file is not None
        and isinstance(qualification_sha256, str)
        and re.fullmatch(r"[0-9a-f]{64}", qualification_sha256) is not None
        and isinstance(max_cost, (int, float))
        and not isinstance(max_cost, bool)
        and max_cost > 0
    ):
        raise ValueError(
            "live mode requires live_authorized, organization_permission_confirmed, "
            "qualification_file, qualification_sha256, and a positive max_total_cost_usd"
        )
    return CampaignConfig(
        schema_version=1,
        campaign_id=campaign_id,
        mode=mode,
        task_ids=tuple(task_ids),
        repetitions=_positive_int(data, "repetitions"),
        seed=data.get("seed") if isinstance(data.get("seed"), int) else 0,
        max_rounds=_positive_int(data, "max_rounds"),
        max_total_runs=_positive_int(data, "max_total_runs"),
        max_concurrency=_positive_int(data, "max_concurrency"),
        agents=agents,
        live_authorized=live_authorized,
        organization_permission_confirmed=organization_permission,
        qualification_file=qualification_file,
        qualification_sha256=qualification_sha256,
        max_total_cost_usd=float(max_cost) if max_cost is not None else None,
    )


def campaign_from_dict(data: dict) -> CampaignConfig:
    agents = {name: AgentConfig(**value) for name, value in data["agents"].items()}
    return CampaignConfig(
        **{key: value for key, value in data.items() if key not in {"agents", "task_ids"}},
        task_ids=tuple(data["task_ids"]),
        agents=agents,
    )
