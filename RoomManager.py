import uuid

from fastapi import WebSocket, WebSocketException, status


class RoomManager:
    def __init__(self) -> None:
        self.__rooms: dict[str, list[WebSocket]] = {}

    def new_room(self) -> str:
        code = self.__generate_code()
        self.__rooms[code] = []
        # print(f"rooms: {self.__rooms}")
        return code


    async def connect(self, code: str, websocket: WebSocket) -> None:
        print("start connection")
        await websocket.accept()
        print("connected")

        if code not in self.__rooms:
            await websocket.close(code=status.WS_1008_POLICY_VIOLATION, reason="Room code is incorrect.")
            raise WebSocketException(code=status.WS_1008_POLICY_VIOLATION, reason="Room code is incorrect.")

        if len(self.__rooms[code]) == 2:
            await websocket.close(code=status.WS_1013_TRY_AGAIN_LATER, reason="Too many connections.")
            raise WebSocketException(code=status.WS_1013_TRY_AGAIN_LATER, reason="Too many connections.")

        self.__rooms[code].append(websocket)
        print(f"rooms: {self.__rooms}")

    async def disconnect(self, code: str, websocket: WebSocket) -> None:
        if code not in self.__rooms:
            raise WebSocketException(code=status.WS_1008_POLICY_VIOLATION, reason="Room code is incorrect.")

        if len(self.__rooms[code]) == 0:
            del self.__rooms[code]
        else:
            self.__rooms[code].remove(websocket)

        if len(self.__rooms[code]) == 0:
            del self.__rooms[code]

    async def send(self, data: dict, websocket: WebSocket) -> None:
        await websocket.send_json(data)

    @staticmethod
    def __generate_code() -> str:
        return str(uuid.uuid4())[:6]
