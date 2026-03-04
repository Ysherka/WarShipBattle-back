import asyncio
import json
import time
from typing import Any

import numpy as np

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
    code: str
    room: list[Game]
    code, room = manager.new_room()

    try:
        await websocket.send_json({"code": code})
        data = await websocket.receive_json()
        user_own_field: list[list[int]] = data["field"]
        print(f"принял первый раз {np.array(user_own_field)}")

        room[1].enemy.username = data["nickname"]
        room[1].enemy.avatar_id = data["photo_index"]

        room[0].add_ships_int(user_own_field)
    except WebSocketDisconnect:
        await websocket.close()


@app.websocket("/join")
async def check_code(websocket: WebSocket):
    await websocket.accept()

    try:
        data: dict = await websocket.receive_json()
        code = data.get("code", None)

        result: bool = manager.is_room_exist(code)
        await websocket.send_json({"success": result})

        data = await websocket.receive_json()
        user_own_field: list[list[int]] = data["field"]

        manager.rooms[code][0].enemy.username = data["nickname"]
        manager.rooms[code][0].enemy.avatar_id = data["photo_index"]

        manager.rooms[code][1].add_ships_int(user_own_field)
    except WebSocketDisconnect:
        await websocket.close()



@app.websocket("/game-{code}")
async def connect_to_game(websocket: WebSocket, code: str):
    user: User
    room: list[Game] = manager.rooms[code]
    await websocket.accept()

    try:
        if not room[0].user.websocket:

            user = manager.rooms[code][0].user
            manager.rooms[code][1].enemy = user
        else:
            user = manager.rooms[code][1].user
            manager.rooms[code][0].enemy = user

        user.websocket = websocket
        # await manager.connect(code, user)

        print(f"перед отправкой {np.array(user.own_field.cells)}")
        response_data = {
            "field": user.own_field.cells,
            "isOwn": True,
        }
        await user.websocket.send_json(response_data)

        while True:
            if room[0].user.websocket and room[1].user.websocket:
                response: dict | None = None
                if room[0].user.websocket == user.websocket:
                    response = {
                        "nickname": room[0].enemy.username,
                        "photo_index": room[0].enemy.avatar_id,
                        "field": room[0].enemy.own_field.cells,
                        "isOwn": False,
                    }
                elif room[1].user.websocket == user.websocket:
                    response = {
                        "nickname": room[1].enemy.username,
                        "photo_index": room[1].enemy.avatar_id,
                        "field": room[0].enemy.own_field.cells,
                        "isOwn": False,
                    }

                await room[0].user.websocket.send_json(response)
                break
    except WebSocketDisconnect:
        await websocket.close()

# вебсокет яйца для аватарки
# @app.websocket("/user")
# async def user(websocket: WebSocket):
#     await websocket.accept()
#
#     # data = None
#     # while data is None:
#     data = await websocket.receive_json()
#     print(data)
#     code: str = data["code"]
#     print("код для получения юзера ", code)
#     room: list[Game] = manager.rooms[code]
#     response: dict
#
#     response1: dict
#     response2: dict
#
#
#     while True:
#         if room[0].user.websocket and room[1].user.websocket:
#             response1 = {
#                 "nickname": room[0].enemy.username,
#                 "photo_index": room[0].enemy.avatar_id
#             }
#             response2 = {
#                 "nickname": room[1].enemy.username,
#                 "photo_index": room[1].enemy.avatar_id
#             }
#             break
#     websocket.send_json([])
#
#     if not room[0].user.info_websocket:
#          response = {
#             "nickname": room[0].enemy.username,
#             "photo_index": room[0].enemy.avatar_id
#         }
#          print("user1: ", response)
#     else:
#         response = {
#             "nickname": room[1].enemy.username,
#             "photo_index": room[1].enemy.avatar_id
#         }
#         print("user2: ", response)
#
#     await websocket.send_json(response)
#     await websocket.close()
