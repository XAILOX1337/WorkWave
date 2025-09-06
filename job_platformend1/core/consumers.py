import json
from channels.generic.websocket import AsyncWebsocketConsumer

class VideoCallConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.room_group_name = f'video_call_{self.room_name}'

        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        data = json.loads(text_data)
        
        # Пересылаем данные всем участникам комнаты
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'video_data',
                'data': data,
                'sender': self.channel_name
            }
        )

    async def video_data(self, event):
        # Отправляем данные только другим участникам
        if event['sender'] != self.channel_name:
            await self.send(text_data=json.dumps(event['data']))