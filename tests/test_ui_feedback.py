"""TV4 feedback behavior in the actual Streamlit app, with the HTTP client mocked."""

from pathlib import Path
from unittest.mock import Mock, call, patch

import pytest
from streamlit.testing.v1 import AppTest

from ui.api_client import AssistantClient

APP = Path(__file__).resolve().parents[1] / "ui" / "app.py"


def feedback_keys(app):
    return {button.key for button in app.button if button.key and button.key.startswith(("up", "down"))}


def toast_messages(app):
    return [toast.proto.body for toast in app.get("toast")]


@pytest.fixture
def feedback_app():
    client = Mock(spec=AssistantClient)
    client.healthy.return_value = True
    client.send_feedback.return_value = True
    with patch("ui.api_client.AssistantClient", return_value=client):
        app = AppTest.from_file(str(APP)).run()
        app.session_state.messages = [
            {"role": "assistant", "content": "Welcome"},
            {"role": "user", "content": "Where is the library?"},
            {"role": "assistant", "content": "Room B.201", "request_id": "request-1"},
        ]
        app.run()
        assert not app.exception
        yield app, client


@pytest.mark.parametrize(
    ("key", "rating", "thanks"),
    [("up2", 1, "Thanks for your feedback!"), ("down2", -1, "Thanks — we will look at this answer.")],
)
def test_successful_vote_is_sent_once_and_survives_reruns(feedback_app, key, rating, thanks):
    app, client = feedback_app
    session_id = app.session_state.session_id
    history = list(app.session_state.messages)
    assert feedback_keys(app) == {"up2", "down2"}

    app.button(key=key).click().run()

    assert not app.exception
    client.send_feedback.assert_called_once_with("request-1", rating)
    assert app.session_state.rated == {"request-1"}
    assert thanks in toast_messages(app)
    assert not feedback_keys(app)

    app.run()
    app.run()
    client.send_feedback.assert_called_once_with("request-1", rating)
    assert not feedback_keys(app)
    assert app.session_state.session_id == session_id
    assert app.session_state.messages == history


@pytest.mark.parametrize(("key", "rating"), [("up2", 1), ("down2", -1)])
def test_failed_vote_remains_unrated_and_can_be_retried(feedback_app, key, rating):
    app, client = feedback_app
    client.send_feedback.return_value = False

    app.button(key=key).click().run()

    assert not app.exception
    assert app.session_state.rated == set()
    assert feedback_keys(app) == {"up2", "down2"}
    assert "Your feedback was not saved. Please try again." in [error.value for error in app.error]
    assert not toast_messages(app)
    client.send_feedback.assert_called_once_with("request-1", rating)

    app.run()
    client.send_feedback.assert_called_once_with("request-1", rating)

    client.send_feedback.return_value = True
    app.button(key=key).click().run()
    assert not app.exception
    assert client.send_feedback.call_args_list == [call("request-1", rating), call("request-1", rating)]
    assert app.session_state.rated == {"request-1"}
    assert not feedback_keys(app)
    assert toast_messages(app)


def test_multiple_answers_have_unique_keys_and_independent_ratings(feedback_app):
    app, client = feedback_app
    app.session_state.messages.extend(
        [
            {"role": "user", "content": "Where do I replace a lost card?"},
            {"role": "assistant", "content": "Student Affairs", "request_id": "request-2"},
        ]
    )
    app.run()
    assert not app.exception
    assert feedback_keys(app) == {"up2", "down2", "up4", "down4"}

    app.button(key="down4").click().run()
    assert not app.exception
    client.send_feedback.assert_called_once_with("request-2", -1)
    assert app.session_state.rated == {"request-2"}
    assert feedback_keys(app) == {"up2", "down2"}

    app.button(key="up2").click().run()
    assert client.send_feedback.call_args_list == [call("request-2", -1), call("request-1", 1)]
    assert app.session_state.rated == {"request-1", "request-2"}
    assert not feedback_keys(app)
    app.run()
    assert client.send_feedback.call_count == 2


def test_messages_without_request_id_offer_no_feedback(feedback_app):
    app, client = feedback_app
    app.session_state.messages = [
        {"role": "assistant", "content": "Welcome"},
        {"role": "user", "content": "Question"},
        {"role": "assistant", "content": "Cannot reach the assistant."},
    ]
    app.run()
    assert not app.exception
    assert not feedback_keys(app)
    client.send_feedback.assert_not_called()


def test_already_rated_answer_does_not_resend_feedback(feedback_app):
    app, client = feedback_app
    app.session_state.rated = {"request-1"}
    app.run()
    assert not app.exception
    assert not feedback_keys(app)
    client.send_feedback.assert_not_called()
