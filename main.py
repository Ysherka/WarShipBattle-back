import numpy as np

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from RoomManager import RoomManager
from bots.Bot import Bot
from game import Game
from models.BotConfig import BotConfig
from models.FieldState import FieldState
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

    try:
        data: dict = await websocket.receive_json()
        print(data)
        bot_difficulty: int | None = data.get("botDifficulty", None)
        if bot_difficulty:
            bot_config: BotConfig = BotConfig(difficulty=bot_difficulty)
            code, room = manager.new_room(bot_config)
        else:
            code, room = manager.new_room()

        await websocket.send_json({"code": code})
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
    await websocket.accept()
    user: User
    room: list[Game] = manager.rooms[code]
    lock = manager.get_lock(code)
    player_index: int = -1

    try:
        async with lock:
            if room[0].user.websocket is None:
                user = room[0].user
                room[0].user.websocket = websocket
                room[1].enemy.websocket = websocket  # для game[1] этот игрок — враг
                player_index = 0
                print("подключился первый игрок")
            elif room[1].user.websocket is None:
                user = room[1].user
                room[1].user.websocket = websocket
                room[0].enemy.websocket = websocket  # для game[0] этот игрок — враг
                player_index = 1
                print("подключился второй игрок")
            else:
                await websocket.close(code=4004, reason="Room is full")
                return

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

        if player_index == 0:
            response = {
                "nickname": room[0].enemy.username,
                "photo_index": room[0].enemy.avatar_id,
                "field": room[0].user.enemy_field.cells,
                "isOwn": False,
                "myTurn": True,
            }
            print("перед отправкой первому игроку врага")
            print(response)

        else:
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
                        is_hit: bool = game.shoot(row, col)
                        if not is_hit:
                            room[0].turn, room[1].turn = room[1].turn, room[0].turn
                        turn: bool = game.turn
                        print(f"был выстрел по координатам {row=}, {col=}")

                        res_field_after_shoot = np.where(
                            game.user.enemy_field.known_cells,
                            game.enemy.own_field.cells,
                            FieldState.EMPTY,
                        )

                        is_win = False
                        if Game.check_all_ships_destroyed(game.enemy.own_field) or \
                                Game.check_all_ships_destroyed(game.user.own_field):
                            is_win = True
                        # print("\nячейки")
                        # print(game.enemy.own_field.cells)
                        # print("\nизвестные ячейки")
                        # print(game.user.enemy_field.known_cells)
                        if is_win:
                            response = {
                                "field": res_field_after_shoot.tolist(),
                                "isOwn": False,
                                "myTurn": turn,
                                "Win": Game.check_all_ships_destroyed(game.enemy.own_field),
                            }
                        else:
                            response = {
                                "field": res_field_after_shoot.tolist(),
                                "isOwn": False,
                                "myTurn": turn,
                            }
                        print("после выстрела перед отправкой")
                        print(response)
                        await user.websocket.send_json(response)

                        if is_win:
                            response2 = {
                                "field": game.enemy.own_field.cells,
                                "isOwn": True,
                                "myTurn": not turn,
                                "Win": Game.check_all_ships_destroyed(game.user.own_field),
                            }
                        else:
                            response2 = {
                                "field": game.enemy.own_field.cells,
                                "isOwn": True,
                                "myTurn": not turn,
                            }
                        await game.enemy.websocket.send_json(response2)


    except WebSocketDisconnect:
        await websocket.close()


@app.websocket("/bot-{code}")
async def bot(websocket: WebSocket, code: str):
    user: User
    bot: Bot
    game: Game = manager.rooms[code][0]
    await websocket.accept()

    try:
        user = game.user
        user.websocket = websocket
        bot = game.bot

        response_data = {
            "field": user.own_field.cells,
            "isOwn": True,
        }
        await user.websocket.send_json(response_data)

        # response: dict= {}
        response = {
            "nickname": bot.name,
            "photo_index": 0,
            "field": user.enemy_field.cells,
            "isOwn": False,
            "myTurn": True,
        }
        await user.websocket.send_json(response)

        while True:
            print("начался основной цикл")
            print(game.turn)
            is_win = False

            if not game.turn:
                row, col = bot.make_move()
                is_hit, destroyed_ship = user.own_field.shoot(row, col, bot.enemy_field)
                bot.register_shot_result(row, col, is_hit, destroyed_ship is not None)

                if not is_hit:
                    game.turn = not game.turn

                if is_win:
                    response2 = {
                        "field": game.user.own_field.cells,
                        "isOwn": True,
                        "myTurn": game.turn,
                        "Win": Game.check_all_ships_destroyed(game.bot.own_field),
                    }
                else:
                    response2 = {
                        "field": game.user.own_field.cells,
                        "isOwn": True,
                        "myTurn": game.turn,
                    }

                await user.websocket.send_json(response2)

                if not game.turn:
                    continue

            data = await user.websocket.receive_json()
            print(f"{data=}")
            if game.turn:
                if "shoot" in data:
                    shoot: tuple[int, int] = data["shoot"]
                    row = shoot[0]
                    col = shoot[1]
                    is_hit: bool = game.shoot_with_bot(row, col)
                    if not is_hit:
                        game.turn = not game.turn

                    print(f"был выстрел по координатам {row=}, {col=}")

                    res_field_after_shoot = np.where(
                        user.enemy_field.known_cells,
                        bot.own_field.cells,
                        FieldState.EMPTY,
                    )

                    if Game.check_all_ships_destroyed(game.bot.own_field) or \
                            Game.check_all_ships_destroyed(game.user.own_field):
                        is_win = True

                    if is_win:
                        response = {
                            "field": res_field_after_shoot.tolist(),
                            "isOwn": False,
                            "myTurn": game.turn,
                            "Win": Game.check_all_ships_destroyed(bot.own_field),
                        }
                    else:
                        response = {
                            "field": res_field_after_shoot.tolist(),
                            "isOwn": False,
                            "myTurn": game.turn,
                        }
                    print("после выстрела перед отправкой")
                    print(response)
                    await user.websocket.send_json(response)




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
