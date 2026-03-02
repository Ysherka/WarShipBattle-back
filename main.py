import asyncio
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


@app.post("/new_game")
async def new_game():
    code: str = manager.new_room()
    return {"code": code}


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

@app.websocket("/game/{code}")
async def connect_to_game(websocket: WebSocket, code: str):
    await manager.connect(code, websocket)
    # user: User = User()
    # user.websocket = websocket
    # user.username = "user2"
    # game: Game = Game()
    # game.user = user

    try:
        while True:
            data = await websocket.receive_json()
            print(f"data: {data}")
            await manager.send(data, websocket)
    except WebSocketDisconnect:
        await manager.disconnect(code, websocket)

