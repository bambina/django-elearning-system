import pytest

from django.urls import path
from channels.routing import URLRouter
from channels.testing import WebsocketCommunicator

from userportal.consumers import *

# Get the auth user model
User = get_user_model()

# Room name for testing
TEST_ROOM_NAME = "test"


@pytest.fixture
def qa_session_fixture(db):
    # Create a QA session for testing
    # TODO: Use factories to create objects
    user = User.objects.create_user(
        username="testuser",
        email="test@example.com",
        password="testpassword",
        first_name="Firstname",
        last_name="Lastname",
        title=PortalUser.Title.PROF,
        user_type=PortalUser.UserType.TEACHER,
    )
    teacher_profile = TeacherProfile.objects.create(
        user=user,
        biography="Prof. Firstname Lastname is a Professor...",
    )
    program = Program.objects.create(
        title="Bachelor of Science in Computer Science",
        description="This 360-credit degree programme...",
    )
    course = Course.objects.create(
        title="Introduction to Computer Science",
        description="This course provides an introduction...",
        program=program,
        teacher=teacher_profile,
    )
    QASession.objects.create(
        course=course,
        room_name=TEST_ROOM_NAME,
    )
    return user, course.id


async def setup_communicator(user: User, course_id: int):
    application = URLRouter(
        [
            path(
                "ws/course/<int:course_id>/live-qa-session/<room_name>/",
                QASessionConsumer.as_asgi(),
            ),
        ]
    )
    url = f"/ws/course/{course_id}/live-qa-session/test/"
    communicator = WebsocketCommunicator(application, url)
    communicator.scope["user"] = user
    connected, _ = await communicator.connect()
    assert connected, "WebSocket connection failed"
    response = await communicator.receive_json_from()
    expected_response = {"type": MESSAGE_TYPE_QUESTION_LIST, "questions": []}
    assert response == expected_response
    return communicator


@pytest.mark.django_db(transaction=True)
@pytest.mark.asyncio
async def test_send_receive_json(qa_session_fixture):
    communicator = await setup_communicator(*qa_session_fixture)
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
async def test_send_receive_json_empty_message(qa_session_fixture):
    communicator = await setup_communicator(*qa_session_fixture)
    await communicator.send_json_to({"message": "", "sender": "user1"})
    assert await communicator.receive_nothing() is True
    await communicator.disconnect()
