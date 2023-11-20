from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse
import json

app = FastAPI()

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

    message_type = message.get("type")

    if message_type == "offer" or message_type == "answer":
        sdp_description = message.get("sdp")
        if sdp_description:
            # Broadcast the SDP description to the other side (client or agent)
            other_role = "agent" if role == "client" else "client"
            for other_id, other_websocket in connected_clients[room_id][f"{other_role}s"].items():
                if other_id != id:
                    await other_websocket.send_text(json.dumps({"type": message_type, "sdp": sdp_description, "id": id}))

    elif message_type == "ice":
        ice_candidate = message.get("ice")
        if ice_candidate:
            # Broadcast the ICE candidate to the other side (client or agent)
            other_role = "agent" if role == "client" else "client"
            for other_id, other_websocket in connected_clients[room_id][f"{other_role}s"].items():
                if other_id != id:
                    await other_websocket.send_text(json.dumps({"type": "ice", "ice": ice_candidate, "id": id}))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="192.168.63.103", port=8282)
