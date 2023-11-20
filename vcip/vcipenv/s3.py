import json
from fastapi import FastAPI,WebSocket,WebSocketDisconnect
import asyncio
app =FastAPI()





user_id = 0
agent_id = 0

active_agents = {}
active_users = {}
id_user_id = {}

agent_user_id = {}

waiting_users = asyncio.Queue()

agent_user_ids = {}

def find_key_by_value(dictionary, value):
    for key, val in dictionary.items():
        if val == value:
            return key
    return None  # Return None if the value is not found in the dictionary

@app.websocket("/ws/client/{u_id}")
async def user_res(websocket: WebSocket, u_id: str):
    await websocket.accept()
    print("USER")
    global user_id
    user_id += 1
    id_user_id[user_id] = u_id
    active_users[user_id] = websocket
    waiting_message_sent = False  # Flag to track if waiting message has been sent
    if user_id > agent_id:
        # response = {"answer":"No agent is available please wait"}
        # await websocket.send_text(response)
        pass
    else:
        # response = {"answer":"You are now connected to an agent"}
        # await websocket.send_text(response)
        pass

    try:
        while True:
            data = await websocket.receive_text()
            try:
                message = json.loads(data)
            except json.JSONDecodeError:
                print("Invalid JSON format")
                return

            message_type = message.get("type")

            if message_type == "offer" or message_type == "answer":
                sdp_description = message.get("sdp")
                print(sdp_description)
            id = find_key_by_value(active_users, websocket)
            agent_socket = active_agents.get(id)
            print(agent_socket)
            
            if agent_socket:
                await agent_socket.send_text(sdp_description)

            
            else:
                await waiting_users.put(websocket)
                if not active_agents:
                    if not waiting_message_sent:  # Send waiting message only once
                        
                        await websocket.send_text({"answer":"No agents available. Please wait."})
                        # logging.info(f"{u_id} waiting for agent")
                        waiting_message_sent = True
                    
                    # Wait for an agent to become available
                    while not active_agents.get(user_id):
                        await asyncio.sleep(1)  # Adjust the sleep duration as needed
                        if waiting_message_sent:
                            await websocket.send_text({"answer":"Please wait for an agent to become available."})
                            waiting_message_sent = False
    except WebSocketDisconnect:
        # active_users.pop(user_id, None)
        agent_socket = active_agents.get(user_id)
        if agent_socket:
            # active_agents.pop(user_id, None)
            await agent_socket.close()
            
    except Exception as e:
        print("Exception occured at user res",e)
        
@app.websocket("/ws/agent/{a_id}")
async def agent_res(websocket: WebSocket, a_id: str):
    await websocket.accept()
    global agent_id
    agent_id += 1
    active_agents[agent_id] = websocket
    
    try:
        # Notify the user that the agent is connected
        id = find_key_by_value(active_agents, websocket)
        fetch_id = id_user_id.get(id)
        agent_user_ids[a_id] = fetch_id
        user_socket = active_users.get(id)
        if user_socket:
            response = {"answer":"An agent is connected."}
            await user_socket.send_text(response)
        
        while True:
            agent_message = await websocket.receive_text()
            print(agent_message)
            id = find_key_by_value(active_agents, websocket)
            user_socket = active_users.get(id)

            if user_socket:
                fetch_id = id_user_id.get(id)
                
                await user_socket.send_text(agent_message)
                # logging.info(f"{a_id} responded to customer query")
              
    except WebSocketDisconnect:
        # active_agents.pop(agent_id, None)
        user_socket = active_users.get(agent_id)
        if user_socket:
            active_users.pop(agent_id, None)
            await user_socket.close()
            # logging.info(f"{agent_id} disconnected")
    except Exception as e:
        print("Exception occured at agnet res",e)
        # logging.error("error occured at agent side")


