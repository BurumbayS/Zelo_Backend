import json
from asgiref.sync import async_to_sync
from channels.generic.websocket import WebsocketConsumer

class TestConsumer(WebsocketConsumer):
    def connect(self):
        Group('users').add(message.reply_channel)

    def disconnect(self, close_code):
        Group('users').discard(message.reply_channel)

    def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json['message']

        self.send(text_data=json.dumps({
            'message': message
        }))
#
# from channels import Group
#
# def ws_connect(message):
#     Group('users').add(message.reply_channel)
#
# def ws_disconnect(message):
#     Group('users').discard(message.reply_channel)
