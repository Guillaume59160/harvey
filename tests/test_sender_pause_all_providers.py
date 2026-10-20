"""Regression tests: emergency pause must cover all outbound email paths."""
from types import SimpleNamespace
from unittest.mock import AsyncMock

import pytest

from harvey.agents.sender import Sender, KILL_SWITCH_KEY


def make_sender(provider):
    state = SimpleNamespace(get_setting=AsyncMock(return_value="operator stop"),
                            get_campaigns_by_status=AsyncMock())
    cfg = SimpleNamespace(channels=SimpleNamespace(
        email=SimpleNamespace(enabled=True, provider=provider)
    ))
    env = SimpleNamespace(instantly_api_key="")
    sender = Sender(brain=None, state=state, config=cfg, env=env)
    return sender, state


@pytest.mark.asyncio
async def test_instantly_run_respects_pause_before_deployment():
    sender, state = make_sender("instantly")
    sender._deploy_campaign = AsyncMock()
    await sender.run()
    state.get_campaigns_by_status.assert_not_awaited()
    sender._deploy_campaign.assert_not_awaited()
    state.get_setting.assert_awaited_with(KILL_SWITCH_KEY)


@pytest.mark.asyncio
async def test_native_run_respects_pause_before_staging():
    sender, state = make_sender("smtp")
    sender._run_native = AsyncMock()
    await sender.run()
    sender._run_native.assert_not_awaited()
    state.get_setting.assert_awaited_with(KILL_SWITCH_KEY)

@pytest.mark.asyncio
async def test_instantly_requires_explicit_autopilot_opt_in():
    sender, state = make_sender("instantly")
    state.get_setting.return_value = None
    sender.config.channels.email.require_approval = True
    sender._deploy_campaign = AsyncMock()
    await sender.run()
    state.get_campaigns_by_status.assert_not_awaited()
    sender._deploy_campaign.assert_not_awaited()
