from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from RoomManager import RoomManager

app = FastAPI()

@app.get("/")
async def main():
    return {"message": "Hello World"}

manager = RoomManager()

@app.post("/game")
async def new_game():
    return manager.new_room()

@app.websocket("/game/{code}")
async def connect_to_game(websocket: WebSocket, code: str):
    await manager.connect(code, websocket)

    try:
        while True:
            data = await websocket.receive_json()
            data["code"] = code
            await manager.send(data, websocket)
    except WebSocketDisconnect:
        await manager.disconnect(code, websocket)

