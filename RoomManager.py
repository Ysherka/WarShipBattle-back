import uuid

from fastapi import WebSocket, WebSocketException, status


class RoomManager:
    def __init__(self) -> None:
        self.__rooms: dict[str, list[WebSocket]] = {}

    def new_room(self) -> str:
        code = self.__generate_code()
        self.__rooms[code] = []
        return code


    async def connect(self, code: str, websocket: WebSocket) -> None:
        await websocket.accept()

        if code not in self.__rooms:
            await websocket.close()
            raise WebSocketException(code=status.WS_1008_POLICY_VIOLATION, reason="Room code is incorrect.")

        if len(self.__rooms[code]) == 2:
            await websocket.close()
            raise WebSocketException(code=status.WS_1013_TRY_AGAIN_LATER, reason="Too many connections.")

        self.__rooms[code].append(websocket)

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

    def __generate_code(self) -> str:
        return str(uuid.uuid4())[:6]
