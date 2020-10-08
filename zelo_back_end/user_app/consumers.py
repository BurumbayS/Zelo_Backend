import json
from asgiref.sync import async_to_sync
from channels.generic.websocket import WebsocketConsumer
from enum import Enum

class MessageType(Enum):
    NEW_ORDER        = "NEW_ORDER"
    DELIVERING_ORDER = "DELIVERING_ORDER"
    COMPLETED_ORDER  = "COMPLETED_ORDER"

class ChatConsumer(WebsocketConsumer):
    def connect(self):
        self.user = self.scope["user"]

        if (self.user.role == "BUSINESS"):
            self.group_name = f'PLACE_{self.user.place_id.id}'
        else:
            self.group_name = f'{self.user.role}'

        print(self.group_name)

        async_to_sync(self.channel_layer.group_add)(
            self.group_name,
            self.channel_name
        )

        self.accept()

    def disconnect(self, close_code):
        async_to_sync(self.channel_layer.group_discard)(
            self.group_name,
            self.channel_name
        )

    def receive(self, text_data):
        text_data_json = json.loads(text_data)
        messageJson = text_data_json['message']
        message = {
            'type': 'chat_message',
            'message': json.dumps(messageJson)
        }

        type = messageJson['type']

        if (type == MessageType.NEW_ORDER.value):
            print(message)
            async_to_sync(self.channel_layer.group_send)('to_ADMIN', message)
            # async_to_sync(self.channel_layer.group_send)('PLACE_1', message)

    def chat_message(self, event):
        message = event['message']

        # Send message to WebSocket
        self.send(text_data=json.dumps({
            'message': message
        }))
