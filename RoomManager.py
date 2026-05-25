import asyncio
import uuid
from dataclasses import asdict

from fastapi import WebSocket, WebSocketException, status

from game import Game
from models.BotConfig import BotConfig
from models.User import User
from bots.Bot import Bot


class RoomManager:
    def __init__(self) -> None:
        self.rooms: dict[str, list[Game]] = {}
        self._locks: dict[str, asyncio.Lock] = {}
        self._conditions: dict[str, asyncio.Condition] = {}

    def get_lock(self, code: str) -> asyncio.Lock:
        if code not in self._locks:
            self._locks[code] = asyncio.Lock()
        return self._locks[code]

    def get_condition(self, code: str) -> asyncio.Condition:
        if code not in self._conditions:
            self._conditions[code] = asyncio.Condition(self.get_lock(code))
        return self._conditions[code]

    def new_room(self, bot_config: BotConfig | None = None) -> tuple[str, list[Game]]:
        code = self.__generate_code().upper()

        if bot_config:
            # Игра против бота
            user = User()
            bot = Bot(**asdict(bot_config))
            bot.place_ships("random")
            self.rooms[code] = [Game(user=user, bot=bot)]
        else:
            # PvP: два игрока
            user1: User = User()
            user2: User = User()
            self.rooms[code] = [Game(user1, user2), Game(user2, user1)]

        return code, self.rooms[code]

    def is_room_exist(self, code: str) -> bool:
        return code in self.rooms

    def is_room_full(self, code: str) -> bool:
        return len(self.rooms[code]) == 2

    async def connect(self, code: str, user: User) -> None:
        print("start connection")
        await user.websocket.accept()
        print("connected")

        if code not in self.rooms:
            await user.websocket.close(code=status.WS_1008_POLICY_VIOLATION, reason="Room code is incorrect.")
            raise WebSocketException(code=status.WS_1008_POLICY_VIOLATION, reason="Room code is incorrect.")

        # if len(self.rooms[code]) == 2:
        #     await user.websocket.close(code=status.WS_1013_TRY_AGAIN_LATER, reason="Too many connections.")
        #     raise WebSocketException(code=status.WS_1013_TRY_AGAIN_LATER, reason="Too many connections.")

        # self.rooms[code].append(game)
        print(f"rooms: {self.rooms}")

    # async def disconnect(self, code: str, user: User) -> None:
    #     if code not in self.rooms:
    #         raise WebSocketException(code=status.WS_1008_POLICY_VIOLATION, reason="Room code is incorrect.")
    #
    #     room = self.rooms[code]
    #
    #     if len(room) == 0:
    #         del room
    #     else:
    #
    #         room.remove(game)
    #
    #     if len(room) == 0:
    #         del room

    @staticmethod
    def __generate_code() -> str:
        return str(uuid.uuid4())[:6]
