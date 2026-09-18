"""Reproducible coding-agent experiment orchestration."""

from .config import AgentConfig, CampaignConfig, load_campaign
from .controller import initialize_campaign, report_campaign, run_campaign, stop_campaign
from .optimization import (
    OptimizationConfig,
    initialize_optimization,
    load_optimization_config,
    report_optimization,
    run_optimization,
    stop_optimization,
)

__all__ = [
    "AgentConfig",
    "CampaignConfig",
    "initialize_campaign",
    "load_campaign",
    "report_campaign",
    "run_campaign",
    "stop_campaign",
    "OptimizationConfig",
    "initialize_optimization",
    "load_optimization_config",
    "report_optimization",
    "run_optimization",
    "stop_optimization",
]
