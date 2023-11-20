import asyncio
import websockets
import json

async def connect_to_server(uri, room_id, role, participant_id):
    async with websockets.connect(uri) as websocket:
        print(f"Connected to server. Room: {room_id}, Role: {role}, ID: {participant_id}")

        # Example: Sending an SDP Offer
        sdp_offer = {
            "type": "offer",
            "sdp": "example_sdp_offer",
        }
        await websocket.send(json.dumps(sdp_offer))
        print(f"Sent SDP Offer: {sdp_offer}")

        # Example: Sending an ICE Candidate
        ice_candidate = {
            "type": "ice",
            "ice": "example_ice_candidate",\
        }
        await websocket.send(json.dumps(ice_candidate))
        print(f"Sent ICE Candidate: {ice_candidate}")

        # Simulate receiving messages
        while True:
            response = await websocket.recv()
            print(f"Received message: {response}")

if __name__ == "__main__":
    # Replace the URI, room_id, role, and participant_id with appropriate values
    uri = "ws://192.168.63.103:8282/ws/room1/client/client1"
    room_id = "room1"
    role = "client"
    participant_id = "client1"

    asyncio.get_event_loop().run_until_complete(connect_to_server(uri, room_id, role, participant_id))
