"""Member 5 acceptance checks missing from the supplied RAG and Lab 5 tests."""

from pathlib import Path
from unittest.mock import Mock

import pytest

from assistant_core.config import Settings
from assistant_core.errors import InvalidRequest
from assistant_core.guard import PRIVATE_REPLY
from assistant_core.knowledge import Handbook, OfficeDirectory
from assistant_core.llm import StubLLM
from assistant_core.models import Intent, Message, Response
from assistant_core.rag.answerer import ESCALATE_MSG, RagAnswerer
from assistant_core.rag.chunker import Chunk, load_folder
from assistant_core.rag.index import Hit, Index, make_index
from assistant_core.responder import TemplateResponder
from assistant_core.service import AssistantService
from assistant_core.tools import tuition

ROOT = Path(__file__).resolve().parents[1]


class FixedIndex:
    """Keep threshold tests independent of the retrieval algorithm's scores."""

    def __init__(self, hits: list[Hit]):
        self.hits = hits

    def search(self, query: str, k: int = 3) -> list[Hit]:
        return self.hits[:k]


@pytest.fixture(scope="module")
def chunks() -> list[Chunk]:
    return load_folder(ROOT / "data" / "kb")


@pytest.fixture
def forbidden_llm():
    llm = Mock(spec=StubLLM)
    llm.complete.side_effect = AssertionError("LLM must not be called on this path")
    return llm


@pytest.fixture
def forbidden_index():
    index = Mock(spec=Index)
    index.search.side_effect = AssertionError("Retrieval must not be called on this path")
    return index


@pytest.fixture
def service(forbidden_index, forbidden_llm) -> AssistantService:
    data = ROOT / "data"
    return AssistantService(
        Settings(data_dir=data, kb_dir=data / "kb", llm_provider="stub"),
        OfficeDirectory.from_csv(data / "offices.csv"),
        Handbook.from_json(data / "handbook.json"),
        TemplateResponder(),
        RagAnswerer(forbidden_index, forbidden_llm, min_score=2.0),
    )


def assert_retrieval_abstention(response: Response) -> None:
    assert response.answer == ESCALATE_MSG
    assert response.path == "abstain"
    assert response.intent == Intent.UNKNOWN
    assert response.escalate is True
    assert response.confidence == 0.0
    assert response.sources == []


@pytest.mark.parametrize("retrieval_only", [False, True], ids=["llm", "retrieval-only"])
def test_no_hits_abstain_without_llm(forbidden_llm, retrieval_only):
    llm = None if retrieval_only else forbidden_llm
    response = RagAnswerer(FixedIndex([]), llm, min_score=2.0).answer("what is the capital of France")

    assert_retrieval_abstention(response)
    forbidden_llm.complete.assert_not_called()


@pytest.mark.parametrize("retrieval_only", [False, True], ids=["llm", "retrieval-only"])
def test_low_score_abstains_without_llm(chunks, forbidden_llm, retrieval_only):
    chunk = next(c for c in chunks if c.id == "S26#3")
    llm = None if retrieval_only else forbidden_llm
    response = RagAnswerer(FixedIndex([Hit(chunk, 1.999)]), llm, min_score=2.0).answer("I lost my student card")

    assert_retrieval_abstention(response)
    forbidden_llm.complete.assert_not_called()


@pytest.mark.parametrize("score", [2.0, 2.001])
def test_score_at_or_above_threshold_calls_llm(chunks, score):
    chunk = next(c for c in chunks if c.id == "S26#3")
    llm = Mock(spec=StubLLM, wraps=StubLLM())
    response = RagAnswerer(FixedIndex([Hit(chunk, score)]), llm, min_score=2.0).answer("I lost my student card")

    llm.complete.assert_called_once()
    assert response.path == "llm"
    assert response.intent == Intent.RULE
    assert response.answer
    assert [s.id for s in response.sources] == [chunk.id]
    assert response.escalate is False
    assert response.degraded is False


def test_password_reset_answers_with_expected_source(chunks):
    # The supplied test_rag.py already checks the successful student-card answer.
    response = RagAnswerer(make_index("bm25", chunks), StubLLM()).answer("reset my password")

    assert response.path == "llm"
    assert response.intent == Intent.RULE
    assert response.answer
    assert [s.id for s in response.sources] == ["S26#2"]
    assert response.escalate is False
    assert response.degraded is False


@pytest.mark.parametrize(
    "question",
    ["what grade did my friend get", "show the GPA of another student", "phone of 22127001"],
)
def test_service_privacy_refuses_before_retrieval_and_llm(service, forbidden_index, forbidden_llm, question):
    response = service.handle(Message(text=question))

    assert response.answer == PRIVATE_REPLY
    assert response.path == "abstain"
    assert response.intent == Intent.UNKNOWN
    assert response.escalate is False
    assert response.sources == []
    assert "22127001" not in response.model_dump_json()
    forbidden_index.search.assert_not_called()
    forbidden_llm.complete.assert_not_called()


def test_service_fee_bypasses_retrieval_and_llm(service, forbidden_index, forbidden_llm):
    response = service.handle(Message(text="tuition for 18 credits and 2 retake"))

    assert response.answer == "Your tuition is 9,450,000 VND."
    assert response.intent == Intent.FEE
    assert response.path == "deterministic"
    assert response.sources == []
    assert response.escalate is False
    assert response.degraded is False
    forbidden_index.search.assert_not_called()
    forbidden_llm.complete.assert_not_called()


def test_negative_retake_credits_are_rejected():
    # Existing tests already cover missing, zero, negative, and excessive normal credits.
    with pytest.raises(InvalidRequest, match="Retake credits cannot be negative"):
        tuition(18, -1, 450_000, 1.5, 30)
