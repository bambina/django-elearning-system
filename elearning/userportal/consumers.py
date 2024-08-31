import json
import datetime
import logging
from typing import Dict

from django.utils import timezone
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async

from userportal.models import *
from userportal.constants import *
from userportal.permissions import *

logger = logging.getLogger(__name__)


class QASessionConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        """Connection event handler provided by AsyncWebsocketConsumer."""
        self.room_name = self.scope["url_route"]["kwargs"]["room_name"]
        self.course_id = self.scope["url_route"]["kwargs"]["course_id"]
        self.room_group_name = f"{LIVE_QA_PREFIX}_{self.room_name}"
        # Join room group
        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        await self.accept()

        # Verify if the user has permission to join the live QA session
        if not await self.has_permission_for_live_qa():
            logger.info(UNAUTHORIZED_ACCESS_MSG)
            await self.close(code=UNAUTHORIZED_ACCESS_CODE)
            return

        if await self.is_qa_session_ended():
            logger.info(QA_SESSION_ENDED_MSG)
            await self.close(code=SESSION_TERMINATE_CODE)
            return

        # Send existing questions to the user
        questions = await self.get_group_questions()
        await self.send(
            text_data=json.dumps(
                {
                    "type": MESSAGE_TYPE_QUESTION_LIST,
                    "questions": [
                        {
                            "message": question.text,
                            "sender": question.sender,
                            "timestamp": question.timestamp.isoformat(),
                        }
                        for question in questions
                    ],
                }
            )
        )

    async def disconnect(self, close_code):
        """Disconnection event handler provided by AsyncWebsocketConsumer."""
        # Leave room group
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    async def receive(self, text_data):
        """Message receive handler provided by AsyncWebsocketConsumer."""
        try:
            data = json.loads(text_data)
            message = data.get("message")
            sender = data.get("sender")
            timestamp = timezone.now()

            if not message:
                logger.info(QA_SESSION_EMPTY_MSG)
                return

            if await self.is_qa_session_ended():
                logger.info(QA_SESSION_ENDED_MSG)
                return

            # Send message to group and save to database
            await self.send_message_to_group(
                MESSAGE_TYPE_QUESTION, message, sender, timestamp
            )
            await self.save_message(message, sender, timestamp)
        except json.JSONDecodeError:
            logger.error(ERR_INVALID_JSON, exc_info=True)
        except Exception as e:
            logger.error(ERR_UNEXPECTED_LOG.format(error=str(e)), exc_info=True)

    async def send_message_to_group(
        self, message_type: str, message: str, sender: str, timestamp: datetime
    ) -> None:
        """Send a message to the group channel."""
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                "type": message_type,
                "message": message,
                "sender": sender,
                "timestamp": timestamp.isoformat(),
            },
        )

    async def question_message(self, message_data: Dict[str, str]) -> None:
        """Send the question to the group"""
        await self.send(
            text_data=json.dumps(
                {
                    "type": MESSAGE_TYPE_QUESTION,
                    "message": message_data["message"],
                    "sender": message_data["sender"],
                    "timestamp": message_data["timestamp"],
                }
            )
        )

    async def close_connection(self, message_data: Dict[str, str]) -> None:
        """Close the connection. This is called when the instructor has ended the QA session"""
        await self.send(
            text_data=json.dumps(
                {
                    "type": MESSAGE_TYPE_CLOSE,
                    "message": message_data["message"],
                    "sender": message_data["sender"],
                    "timestamp": message_data["timestamp"],
                }
            )
        )
        # Close the connection
        await self.close(code=SESSION_TERMINATE_CODE)

    @database_sync_to_async
    def save_message(self, message: str, sender: str, timestamp: datetime) -> None:
        """Save the message to the database"""
        qa_question = QAQuestion(
            room_name=self.room_name, text=message, sender=sender, timestamp=timestamp
        )
        qa_question.save()

    @database_sync_to_async
    def get_group_questions(self) -> list[QAQuestion]:
        """Get all questions in the group"""
        return list(
            QAQuestion.objects.filter(room_name=self.room_name).order_by("timestamp")
        )

    @database_sync_to_async
    def is_qa_session_ended(self) -> bool:
        """Check if the QA session is ended"""
        qa_session = QASession.objects.filter(room_name=self.room_name).first()
        # If the session does not exist or its status is ENDED, return True
        return not qa_session or qa_session.status == QASession.Status.ENDED

    @database_sync_to_async
    def has_permission_for_live_qa(self) -> bool:
        """Check if the user has permission to join the live QA session"""
        course = Course.objects.filter(id=self.course_id).first()
        if not course:
            return False
        user = self.scope["user"]
        return PermissionChecker.is_active_in_course(user, course)
