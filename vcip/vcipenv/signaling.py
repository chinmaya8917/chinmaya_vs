from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse
import json

app = FastAPI()

connected_clients = {}

@app.get("/")
async def get():
    return HTMLResponse(content="<h1>FastAPI Signaling Server</h1>")

@app.websocket("/ws/{room_id}")
async def websocket_endpoint(websocket: WebSocket, room_id: str):
    await websocket.accept()
    
    if room_id not in connected_clients:
        connected_clients[room_id] = set()
    
    connected_clients[room_id].add(websocket)
    
    try:
        while True:
            data = await websocket.receive_text()
            print(f"Received message from room {room_id}: {data}")
            
            await process_signaling_data(websocket, room_id, data)
    except WebSocketDisconnect:
        connected_clients[room_id].remove(websocket)
        if not connected_clients[room_id]:
            del connected_clients[room_id]

async def process_signaling_data(websocket: WebSocket, room_id: str, data: str):
    # Parse the received JSON data
    try:
        message = json.loads(data)
    except json.JSONDecodeError:
        print("Invalid JSON format")
        return

    message_type = message.get("type")

    if message_type == "offer" or message_type == "answer":
        # SDP Offer or Answer
        sdp_description = message.get("sdp")
        if sdp_description:
            # Broadcast the SDP description to other clients in the room
            await broadcast_sdp_description(websocket, room_id, sdp_description)

    elif message_type == "ice":
        # ICE Candidate
        ice_candidate = message.get("ice")
        if ice_candidate:
            # Broadcast the ICE candidate to other clients in the room
            await broadcast_ice_candidate(websocket, room_id, ice_candidate)

    # Handle other types of messages if needed

async def broadcast_sdp_description(sender_websocket: WebSocket, room_id: str, sdp_description: str):
    # Broadcast the SDP description to other clients in the room
    for connected_websocket in connected_clients[room_id]:
        if connected_websocket != sender_websocket:
            await connected_websocket.send_text(json.dumps({"type": "sdp", "sdp": sdp_description}))

async def broadcast_ice_candidate(sender_websocket: WebSocket, room_id: str, ice_candidate: str):
    # Broadcast the ICE candidate to other clients in the room
    for connected_websocket in connected_clients[room_id]:
        if connected_websocket != sender_websocket:
            await connected_websocket.send_text(json.dumps({"type": "ice", "ice": ice_candidate}))



if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="192.168.63.103", port=8282)