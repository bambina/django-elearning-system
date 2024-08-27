import json

from channels.generic.websocket import AsyncWebsocketConsumer
from .constants import *
from userportal.models import *
from channels.db import database_sync_to_async
from django.utils import timezone
from userportal.permissions import *


class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_name = self.scope["url_route"]["kwargs"]["room_name"]
        self.room_group_name = f"{LIVE_QA_PREFIX}_{self.room_name}"

        # Join room group
        await self.channel_layer.group_add(self.room_group_name, self.channel_name)

        await self.accept()

        # Send existing messages
        questions = await self.get_questions()
        await self.send(
            text_data=json.dumps(
                {
                    "type": "question.list",
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
        # Leave room group
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    # Receive message from WebSocket
    async def receive(self, text_data):
        try:
            data = json.loads(text_data)
            message = data.get("message")
            sender = data.get("sender")
            timestamp = timezone.now()

            if not (message and sender):
                # TODO: Log the error
                return

            if await self.is_session_ended():
                return

            # Send message to room group
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    "type": "question.message",
                    "message": message,
                    "sender": sender,
                    "timestamp": timestamp.isoformat(),
                },
            )

            # Save message to database
            await self.save_message(message, sender, timestamp)
        except Exception:
            # TODO: Log the error
            pass

    # Receive message from room group
    async def question_message(self, event):
        message = event["message"]
        sender = event["sender"]
        timestamp = event["timestamp"]

        # Send message to WebSocket
        await self.send(
            text_data=json.dumps(
                {"message": message, "sender": sender, "timestamp": timestamp}
            )
        )

    async def close_connection(self, event):
        # Send close message
        message = event["message"]
        sender = event["sender"]
        timestamp = event["timestamp"]

        await self.send(
            text_data=json.dumps(
                {
                    "type": "session.end.notice",
                    "message": message,
                    "sender": sender,
                    "timestamp": timestamp,
                }
            )
        )
        # Close the connection
        await self.close(code=4000)

    @database_sync_to_async
    def save_message(self, message, sender, timestamp):
        chat_msg = QAQuestion(
            room_name=self.room_name, text=message, sender=sender, timestamp=timestamp
        )
        chat_msg.save()

    @database_sync_to_async
    def get_questions(self):
        return list(
            QAQuestion.objects.filter(room_name=self.room_name).order_by("-timestamp")
        )

    @database_sync_to_async
    def is_session_ended(self):
        qa_session = QASession.objects.filter(room_name=self.room_name).first()
        return qa_session and qa_session.status == QASession.Status.ENDED
