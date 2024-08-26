import json

from channels.generic.websocket import AsyncWebsocketConsumer
from .constants import *
from datetime import datetime


class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_name = self.scope["url_route"]["kwargs"]["room_name"]
        self.room_group_name = f"{LIVE_QA_PREFIX}_{self.room_name}"

        # Join room group
        await self.channel_layer.group_add(self.room_group_name, self.channel_name)

        await self.accept()

    async def disconnect(self, close_code):
        # Leave room group
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    # Receive message from WebSocket
    async def receive(self, text_data):
        try:
            data = json.loads(text_data)
            message = data.get("message")
            sender = data.get("sender")
            timestamp = data.get("timestamp")

            if not (message and sender and timestamp):
                # TODO: Log the error
                return

            # Send message to room group
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    "type": "chat.message",
                    "message": message,
                    "sender": sender,
                    "timestamp": timestamp,
                },
            )
        except Exception:
            # TODO: Log the error
            pass

    # Receive message from room group
    async def chat_message(self, event):
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
        # Send close message to room group
        await self.send(
            text_data=json.dumps(
                {
                    "type": "session.end.notice",
                    "message": "The QA session has ended.",
                    "sender": "System",
                    "timestamp": datetime.now().strftime("%Y-%m-%dT%H:%M:%S.%fZ"),
                }
            )
        )
        # Close the connection
        await self.close()
