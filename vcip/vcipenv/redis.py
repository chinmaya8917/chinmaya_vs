from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse
import json
import aioredis

app = FastAPI()

# Create a Redis connection pool
redis_pool = None  # Replace with your Redis connection details

@app.on_event("startup")
async def startup():
    global redis_pool
    redis_pool = await aioredis.create_redis_pool("redis://127.0.0.1:6379", encoding='utf-8')



@app.on_event("shutdown")
async def shutdown():
    global redis_pool
    if redis_pool:
        redis_pool.close()
        await redis_pool.wait_closed()

connected_clients = {}

@app.get("/")
async def get():
    return HTMLResponse(content="<h1>FastAPI Signaling Server</h1>")

@app.websocket("/ws/{room_id}/{role}/{id}")
async def websocket_endpoint(websocket: WebSocket, room_id: str, role: str, id: str):
    await websocket.accept()

    if room_id not in connected_clients:
        connected_clients[room_id] = {"clients": {}, "agents": {}}

    connected_clients[room_id][f"{role}s"][id] = websocket

    try:
        while True:
            data = await websocket.receive_text()
            print(f"Received message from {role} {id} in room {room_id}: {data}")

            await process_signaling_data(websocket, room_id, role, id, data)
    except WebSocketDisconnect:
        del connected_clients[room_id][f"{role}s"][id]
        if not connected_clients[room_id]["clients"] and not connected_clients[room_id]["agents"]:
            del connected_clients[room_id]

async def process_signaling_data(websocket: WebSocket, room_id: str, role: str, id: str, data: str):
    try:
        message = json.loads(data)
    except json.JSONDecodeError:
        print("Invalid JSON format")
        return

    print(f"Received message from {role} {id} in room {room_id}: {message}")

    message_type = message.get("type")
    sender_role = message.get("sender_role")

    if not message_type or not sender_role:
        print("Missing required fields in the message.")
        return

    if sender_role not in ["client", "agent"]:
        print("Invalid sender role in the message.")
        return

    if message_type == "offer" or message_type == "answer" or message_type == "ice":
        # Store the message in Redis for broadcasting
        await redis_pool.publish(room_id, json.dumps({
            "type": message_type,
            "data": message,
            "id": id,
            "sender_role": sender_role
        }))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="192.168.63.103", port=8282)
