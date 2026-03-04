import uuid

from fastapi import WebSocket, WebSocketException, status

from game import Game
from models.User import User


class RoomManager:
    def __init__(self) -> None:
        self.rooms: dict[str, list[Game]] = {}

    def new_room(self) -> str:
        code = self.__generate_code().upper()
        self.rooms[code] = [Game(User(), User()), Game(User(), User())]
        return code

    def is_room_exist(self, code: str) -> bool:
        print(self.rooms)
        return code in self.rooms

    def is_room_full(self, code: str) -> bool:
        return len(self.rooms[code]) == 2

    def add_users_to_games(self, code: str, user1: User, user2: User, game1: Game, game2: Game) -> None:
        game1.user = user1
        game1.enemy = user2
        game2.user = user2
        game2.enemy = user1

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

    async def disconnect(self, code: str, game: Game) -> None:
        if code not in self.rooms:
            raise WebSocketException(code=status.WS_1008_POLICY_VIOLATION, reason="Room code is incorrect.")

        if len(self.rooms[code]) == 0:
            del self.rooms[code]
        else:
            self.rooms[code].remove(game)

        if len(self.rooms[code]) == 0:
            del self.rooms[code]

    # async def send(self, data: dict, websocket: WebSocket) -> None:
    #     await websocket.send_json(data)

    @staticmethod
    def __generate_code() -> str:
        return str(uuid.uuid4())[:6]
