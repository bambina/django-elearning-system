import pytest
from typing import Type
from channels.routing import URLRouter
from channels.testing import WebsocketCommunicator

from django.urls import path
from django.contrib.auth import get_user_model
from django.contrib.auth.models import AnonymousUser

from userportal.consumers import *
from userportal.tests.model_factories import *

# Get the auth user model
AuthUserType = Type[get_user_model()]


@pytest.fixture
def active_qa_session_fixture(db):
    # Create an active QA session along with related entities.
    return QASessionFactory.create()


@pytest.fixture
def ended_qa_session_fixture(db):
    # Create an ended QA session along with related entities.
    return QASessionFactory.create(status=QASession.Status.ENDED)


@pytest.fixture
def active_qa_session_with_unenrolled_student_fixture(db):
    # Create an active QA session, and a student not enrolled in the course.
    qa_session = QASessionFactory.create()
    student = StudentProfileFactory.create()
    return qa_session, student.user


async def setup_communicator(
    qa_session: QASession, user: AuthUserType = None
) -> WebsocketCommunicator:
    """Setup a WebSocket communicator for the QA session."""
    course = qa_session.course
    request_user = user if user else course.teacher.user
    room_name = qa_session.room_name
    application = URLRouter(
        [
            path(
                "ws/course/<int:course_id>/live-qa-session/<room_name>/",
                QASessionConsumer.as_asgi(),
            ),
        ]
    )
    url = f"/ws/course/{course.id}/live-qa-session/{room_name}/"
    communicator = WebsocketCommunicator(application, url)
    communicator.scope["user"] = request_user
    return communicator


async def connect_and_get_questions(communicator) -> None:
    """Connect to the WebSocket and get the existing questions."""
    connected, _ = await communicator.connect()
    assert connected, "WebSocket connection failed"
    response = await communicator.receive_json_from()
    expected_response = {"type": MESSAGE_TYPE_QUESTION_LIST, "questions": []}
    assert response == expected_response


@pytest.mark.django_db(transaction=True)
@pytest.mark.asyncio
async def test_send_receive_json(active_qa_session_fixture):
    """Test sending and receiving JSON messages."""
    communicator = await setup_communicator(active_qa_session_fixture)
    await connect_and_get_questions(communicator)
    message_text = "hello"
    sender = "user1"
    await communicator.send_json_to({"message": message_text, "sender": sender})
    response = await communicator.receive_json_from()
    assert response["type"] == MESSAGE_TYPE_QUESTION
    assert response["message"] == message_text
    assert response["sender"] == sender
    await communicator.disconnect()


@pytest.mark.django_db(transaction=True)
@pytest.mark.asyncio
async def test_receive_nothing_for_empty_message(active_qa_session_fixture):
    """Test that the consumer does not respond to empty messages."""
    communicator = await setup_communicator(active_qa_session_fixture)
    await connect_and_get_questions(communicator)
    await communicator.send_json_to({"message": "", "sender": "user1"})
    assert await communicator.receive_nothing() is True
    await communicator.disconnect()


@pytest.mark.django_db(transaction=True)
@pytest.mark.asyncio
async def test_deny_connect_for_ended_session(ended_qa_session_fixture):
    """Test that the consumer denies connection for an ended QA session."""
    communicator = await setup_communicator(ended_qa_session_fixture)
    await communicator.connect()
    response = await communicator.receive_output()
    expected_response = {"type": "websocket.close", "code": SESSION_TERMINATE_CODE}
    assert response == expected_response
    await communicator.disconnect()


@pytest.mark.django_db(transaction=True)
@pytest.mark.asyncio
async def test_deny_connect_for_unenrolled_student(
    active_qa_session_with_unenrolled_student_fixture,
):
    """Test that the consumer denies connection for an unenrolled student."""
    communicator = await setup_communicator(
        *active_qa_session_with_unenrolled_student_fixture
    )
    await communicator.connect()
    response = await communicator.receive_output()
    expected_response = {"type": "websocket.close", "code": UNAUTHORIZED_ACCESS_CODE}
    assert response == expected_response
    await communicator.disconnect()


@pytest.mark.django_db(transaction=True)
@pytest.mark.asyncio
async def test_deny_connect_for_unauthenticated_user(
    active_qa_session_fixture,
):
    """Test that the consumer denies connection for an unauthenticated user."""
    communicator = await setup_communicator(
        active_qa_session_fixture, user=AnonymousUser()
    )
    await communicator.connect()
    response = await communicator.receive_output()
    expected_response = {"type": "websocket.close", "code": UNAUTHORIZED_ACCESS_CODE}
    assert response == expected_response
    await communicator.disconnect()
