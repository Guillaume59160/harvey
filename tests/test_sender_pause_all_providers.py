"""Regression tests: pause switch must cover all mail delivery paths."""
from unittest.mock import AsyncMock

import pytest

from harvey.agents.sender import Sender, KILL_SWITCH_KEY


class DummyEmail:
    enabled = True
    provider = "instantly"


class DummyChannels:
    email = DummyEmail()


class DummyConfig:
    channels = DummyChannels()


class DummyEnv:
    instantly_api_key = ""


@pytest.mark.asyncio
async def test_instantly_run_respects_pause_before_deployment():
    state = AsyncMock()
    state.get_setting.return_value = "operator emergency stop"
    sender = Sender(brain=None, state=state, config=DummyConfig(), env=DummyEnv())
    sender._deploy_campaign = AsyncMock()
    await sender.run()
    state.get_campaigns_by_status.assert_not_awaited()
    sender._deploy_campaign.assert_not_awaited()
    state.get_setting.assert_awaited_with(KILL_SWITCH_KEY)


@pytest.mark.asyncio
async def test_native_run_respects_pause_before_staging():
    state = AsyncMock()
    state.get_setting.return_value = "operator emergency stop"
    sender = Sender(brain=None, state=state, config=DummyConfig(), env=DummyEnv())
    sender.is_native  # evaluated with Instantly config; use a test-only native provider
    sender.config.channels.email.provider = "smtp"
    sender.provider = AsyncMock()
    sender._run_native = AsyncMock()
    try:
        await sender.run()
        sender._run_native.assert_not_awaited()
    finally:
        sender.config.channels.email.provider = "instantly"
