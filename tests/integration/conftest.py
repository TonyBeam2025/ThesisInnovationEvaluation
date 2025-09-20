from __future__ import annotations

import pytest

INTEGRATION_SKIP_REASON = "integration tests require manual setup (API keys, large data)"


def pytest_collection_modifyitems(config: pytest.Config, items: list[pytest.Item]) -> None:
    for item in items:
        if item.nodeid.startswith("tests/integration/"):
            item.add_marker(pytest.mark.skip(reason=INTEGRATION_SKIP_REASON))
