import base64
import json
import secrets

from asgiref.sync import async_to_sync
from channels.generic.websocket import WebsocketConsumer
from django.core.files.base import ContentFile

from matrimonials.models import Conversation, Message
from matrimonials.serializers import MessageSerializer


class ConversationConsumer(WebsocketConsumer):
    def __init__(self, *args, **kwargs):
        super().__init__(args, kwargs)
        self.room_name = None
        self.room_group_name = None

    def connect(self):
        print('here')
        self.room_name = self.scope["url_route"]["kwargs"]["room_name"]
        self.room_group_name = f"conversation_{self.room_name}"

        # Join room group
        async_to_sync(self.channel_layer.group_add)(
                self.room_group_name, self.channel_name
        )
        self.accept()

    def disconnect(self, close_code):
        # Leave room group
        async_to_sync(self.channel_layer.group_discard)(
                self.room_group_name, self.channel_name
        )

    # Receive message from WebSocket
    def receive(self, text_data=None, bytes_data=None):
        # parse the json data into dictionary object
        text_data_json = json.loads(text_data)

        # Send message to room group
        conversation_type = {"type": "conversation_message"}
        return_dict = {**conversation_type, **text_data_json}
        async_to_sync(self.channel_layer.group_send)(
                self.room_group_name,
                return_dict,
        )

    # Receive messages from room group
    def conversation_message(self, event):
        text_data_json = event.copy()
        text_data_json.pop("type")
        message, attachment = (
            text_data_json["conversation_message"],
            text_data_json.get("attachment"),
        )

        conversation = Conversation.objects.get(id=str(self.room_name))
        sender = self.scope['user']

        # Attachment
        if attachment:
            file_str, file_ext = attachment["data"], attachment["format"]

            file_data = ContentFile(
                    base64.b64decode(file_str), name=f"{secrets.token_hex(8)}.{file_ext}"
            )
            _message = Message.objects.create(
                    sender=sender,
                    attachment=file_data,
                    text=message,
                    conversation_id=conversation,
            )
        else:
            _message = Message.objects.create(
                    sender=sender,
                    text=message,
                    conversation_id=conversation,
            )
        serializer = MessageSerializer(instance=_message)
        # Send message to WebSocket
        self.send(
                text_data=json.dumps(
                        serializer.data
                )
        )
