from pydantic import BaseModel
from fastapi import WebSocket

from models.Field import BaseField, OwnField, EnemyField


# class UserBase():
#     username: str
#     websocket: WebSocket
#
class User:
    def __init__(self):
        self.avatar_id: int = 0
        self.username: str | None = None
        self.websocket: WebSocket | None = None
        self.info_websocket: WebSocket | None = None
        self.own_field: OwnField = OwnField()
        self.enemy_field: EnemyField = EnemyField()
