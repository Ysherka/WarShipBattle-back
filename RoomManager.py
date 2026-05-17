import uuid

from fastapi import WebSocket, WebSocketException, status

from game import Game
from models.User import User
from bots.Bot import Bot


class RoomManager:
    def __init__(self) -> None:
        self.rooms: dict[str, list[Game]] = {}

    def new_room(self, with_bot: bool = False) -> str:
        code = self.__generate_code().upper()
        
        if with_bot:
            # Игра против бота
            user = User()
            bot = Bot(name="AI", difficulty=1)
            bot.place_ships("random")
            self.rooms[code] = [Game(user=user, bot=bot)]
        else:
            # PvP: два игрока
            self.rooms[code] = [Game(User(), User()), Game(User(), User())]
        
        return code

    def is_room_exist(self, code: str) -> bool:
        return code in self.rooms

    def is_room_full(self, code: str) -> bool:
        return len(self.rooms[code]) == 2

    def add_users_to_games(self, code: str, user1: User, user2: User, game1: Game, game2: Game) -> None:
        game1.user = user1
        game1.enemy = user2
        game2.user = user2
        game2.enemy = user1

    async def connect(self, code: str, user: User) -> None:
        if code not in self.rooms:
            await user.websocket.close(code=status.WS_1008_POLICY_VIOLATION, reason="Room code is incorrect.")
            raise WebSocketException(code=status.WS_1008_POLICY_VIOLATION, reason="Room code is incorrect.")

    async def disconnect(self, code: str, game: Game) -> None:
        if code not in self.rooms:
            raise WebSocketException(code=status.WS_1008_POLICY_VIOLATION, reason="Room code is incorrect.")

        if game in self.rooms[code]:
            self.rooms[code].remove(game)

        if len(self.rooms[code]) == 0:
            del self.rooms[code]

    @staticmethod
    def __generate_code() -> str:
        return str(uuid.uuid4())[:6]