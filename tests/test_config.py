
from src.config import (
    EMBEDDING_MODEL,
    MAX_RETRIES,
    OPENAI_MODEL,
    TOP_K,
)


def test_configuration():
    assert OPENAI_MODEL
    assert EMBEDDING_MODEL
    assert TOP_K > 0
    assert MAX_RETRIES >= 0
