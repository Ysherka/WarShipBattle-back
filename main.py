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

        room[0].user.username = data["nickname"]
        room[0].user.avatar_id = data["photo_index"]
        room[0].turn = True

        room[0].add_ships_int(user_own_field)
    except WebSocketDisconnect:
        await websocket.close()


@app.websocket("/join")
async def join(websocket: WebSocket):
    await websocket.accept()

    try:
        data: dict = await websocket.receive_json()
        code = data.get("code", None)

        result: bool = manager.is_room_exist(code)
        await websocket.send_json({"success": result})

        data = await websocket.receive_json()
        user_own_field: list[list[int]] = data["field"]

        manager.rooms[code][1].user.username = data["nickname"]
        manager.rooms[code][1].user.avatar_id = data["photo_index"]
        manager.rooms[code][1].turn = False

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
            print("первый получил вебсокет")
            user = manager.rooms[code][0].user
            manager.rooms[code][1].enemy.websocket = user.websocket
        else:
            print("второй получил вебсокет")
            user = manager.rooms[code][1].user
            manager.rooms[code][0].enemy.websocket = user.websocket

        user.websocket = websocket

        if room[0].user.websocket == user.websocket:
            print("первый игрок")
        else:
            print("Второй игрок")

        # print(f"перед отправкой {np.array(user.own_field.cells)}")
        print(f"перед отправкой собственного поля")
        response_data = {
            "field": user.own_field.cells,
            "isOwn": True,
        }
        await user.websocket.send_json(response_data)

        user.is_ready.set()

        await room[0].user.is_ready.wait()
        print("первый готов")
        await room[1].user.is_ready.wait()
        print("второй готов")

        response: dict | None = {}

        # for i, game in enumerate(room):
        #     if game.user == user.websocket:
        #         response = {
        #             "nickname": game.enemy.username,
        #             "photo_index": game.enemy.avatar_id,
        #             "field": game.enemy.own_field.cells,
        #             "isOwn": False,
        #             "myTurn": i == 0,
        #         }
        #         print(f"перед отправкой {i+1}-му игроку врага")
        #         print(response)
        #
        # await user.websocket.send_json(response)

        if room[0].user.websocket == user.websocket:
            response = {
                "nickname": room[0].enemy.username,
                "photo_index": room[0].enemy.avatar_id,
                "field": room[0].user.enemy_field.cells,
                "isOwn": False,
                "myTurn": True,
            }
            print("перед отправкой первому игроку врага")
            print(response)

        elif room[1].user.websocket == user.websocket:
            response = {
                "nickname": room[1].enemy.username,
                "photo_index": room[1].enemy.avatar_id,
                "field": room[1].user.enemy_field.cells,
                "isOwn": False,
                "myTurn": False,
            }
            print("перед отправкой второму игроку врага")
            print(response)

        await user.websocket.send_json(response)

        while True:
            print("начался основной цикл")
            data = await user.websocket.receive_json()
            print(f"{data=}")
            # {shoot: [x, y]}
            if "shoot" in data:
                shoot: tuple[int, int] = data["shoot"]
                row = shoot[0]
                col = shoot[1]
                for game in room:
                    if game.user.websocket == user.websocket:
                        # game.shoot()
                        room[0].turn, room[1].turn = room[1].turn, room[0].turn
                        turn: bool = game.turn
                        print(f"был выстрел по координатам {row=}, {col=}")
                        response = {
                            "field": game.user.enemy_field.cells,
                            "isOwn": False,
                            "myTurn": turn,
                        }
                        print("после выстрела перед отправкой")
                        print(response)
                        await user.websocket.send_json(response)

                        response2 = {
                            "field": game.enemy.own_field.cells,
                            "isOwn": True,
                            "myTurn": not turn,
                        }
                        await game.enemy.websocket.send_json(response2)


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
