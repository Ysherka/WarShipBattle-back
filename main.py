import asyncio
import json
import time
from typing import Any

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from RoomManager import RoomManager
from game import Game
from models.User import User

app = FastAPI()

@app.get("/")
async def main():
    return {"message": "Hello World"}

manager = RoomManager()


@app.websocket("/game")
async def new_game(websocket: WebSocket):
    await websocket.accept()
    code: str = manager.new_room()

    try:
        await websocket.send_json({"code": code})

        data = await websocket.receive_json()
        user_own_field: list[list[int]] = data
        print(Game.field_to_ship_list(user_own_field))

        manager.rooms[code][0].add_ships_int(user_own_field)
    except WebSocketDisconnect:
        await websocket.close()


@app.websocket("/join")
async def check_code(websocket: WebSocket):
    await websocket.accept()

    try:
        data: dict[str, str] = await websocket.receive_json()
        code: str | None = data.get("code", None)
        print(code)
        result: bool = manager.is_room_exist(code)
        await websocket.send_json({"success": result})

        data: list[list[int]] = await websocket.receive_json()
        user_own_field: list[list[int]] = data

        manager.rooms[code][1].add_ships_int(user_own_field)
    except WebSocketDisconnect:
        await websocket.close()


@app.websocket("/game-{code}")
async def connect_to_game(websocket: WebSocket, code: str):
    user: User
    if not manager.rooms[code][0].user.websocket:
        user = manager.rooms[code][0].user
    else:
        user = manager.rooms[code][1].user
    user.websocket = websocket
    await manager.connect(code, user)

    try:
        response_data = {
            "field": user.own_field.cells,
            "isOwn": True
        }
        # print(response_data)
        print(json.dumps(response_data))
        await websocket.send_json(response_data)
        # while True:
        #     data = await websocket.receive_json()
        #     print(data)
    except WebSocketDisconnect:
        await manager.disconnect(code, user)


# @app.websocket("/game")
# async def new_game(websocket: WebSocket):
#     code: str = await manager.new_room(websocket)
#     # user: User = User()
#     # user.websocket = websocket
#     # user.username = "user1"
#     # game: Game = Game()
#     # game.user = user
#
#     try:
#         await websocket.send_json({"code": code})
#         while True:
#             data = await websocket.receive_json()
#             print(f"data: {data}")
#
#             user1_own_field: list[list[int]] = data
#             print(Game.field_to_ship_list(user1_own_field))
#             # game.add_ships(Game.field_to_ship_list(user1_own_field))
#             #
#             # if "shoot" in data:
#             #     game.shoot(data["x"], data["y"])
#
#
#     except WebSocketDisconnect:
#         await manager.disconnect(code, websocket)


# /game-{code}
