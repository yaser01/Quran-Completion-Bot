import pytest


@pytest.fixture
def sample_db_uri():
    return "postgresql+asyncpg://test:test@localhost:5432/quranbot_test"
