from flask import Flask, request, jsonify
import requests
import threading
import sys
import time
import logging
import random
from colors import log
app = Flask(__name__)

# Global variables
server_id = None              # Unique identifier for this server
current_port = None              # Unique identifier for this server
next_server_url = None        # URL of the next server in the ring
prev_server_url = None        # URL of the previous server in the ring
server_data = []

logger = logging.getLogger("werkzeug")
logger.setLevel(logging.ERROR)

@app.route('/status', methods=['GET'])
def status():
    """Return the server status."""
    return jsonify({
        "server_id": server_id,
        "next_server_url": next_server_url,
        "prev_server_url": prev_server_url
    }), 200

@app.route('/process', methods=['POST'])
def process():
    """Process incoming tasks and add to the queue."""
    global server_data
    data = request.json
    tasks = data.get("tasks")
    client = data.get("client_url")

    log("CYAN",f"{server_id}:{current_port} received new tasks from client : {tasks}")
    if not tasks or client is None:
        return jsonify({"error": "Tasks and client URL are required"}), 400
    # Process the tasks

    server_data.extend(tasks)
    return jsonify({"message": f"Tasks added to the queue: {tasks}"}), 200

def start_heartbeat():
    """Continuously send heartbeats to the next server."""
    global next_server_url, server_id, server_data, current_port
    time.sleep(2)  # Send heartbeat every 2 seconds
    if next_server_url:
        try:
            requests.post(f"http://{next_server_url}/heartbeat", json={"origin": server_id,"tasks": [],"counter" : {server_id : 0}}, timeout=5)
        except Exception as e:
            print(f"[ERROR] {server_id}: Failed to send heartbeat to {next_server_url}: {e}")


    

@app.route('/heartbeat', methods=['POST'])
def heartbeat():
    """Handle incoming heartbeat."""
    time.sleep(2)
    global server_data, server_id
    data = request.json
    origin = data.get("origin")
    tasks = data.get("tasks",[])
    counter = data.get("counter",{})
    curr_length = len(server_data)
    counter[server_id] = curr_length
    total = sum(counter.values())+len(tasks)
    perserver = total//4
    extra  = total % 4
    needed = perserver - curr_length
    if needed>0:
        server_data.extend(tasks[:needed])
        tasks = tasks[needed:]
        counter[server_id] = len(server_data)
    elif needed<0:
        needed = abs(needed)
        tasks.extend(server_data[perserver:])
        server_data = server_data[:perserver]
        counter[server_id] = len(server_data)

    if extra > 0 and len(tasks) > 0:
        server_data.extend(tasks.pop(0))
        counter[server_id] = len(server_data)
    if len(server_data) > 0:
        log("YELLOW",f"{server_id}:{current_port} Local Tasks : {server_data}")
    # Forward the heartbeat to the next server
    if next_server_url:
        try:
            if len(tasks):
                log("MAGENTA",f"{server_id} {current_port} sending extra tasks {tasks} to {next_server_url}")
            threading.Thread(
                target=lambda: requests.post(f"http://{next_server_url}/heartbeat", json={"origin": server_id,"tasks": tasks,"counter": counter}, timeout=5)
            ).start()
        except Exception as e:
            print(f"[ERROR] Failed to forward heartbeat to {next_server_url}: {e}")
    return jsonify({"message": f"Heartbeat processed by {server_id}"}), 200

def start_execution():
    while(True):
        if len(server_data)>0:
            # time.sleep(random.randint(1,int(server_data[0])))
            execution_value = server_data[0]
            log("GREEN",f"{server_id} {current_port} Executing tasks : {execution_value}")
            time.sleep(5)
            server_data.pop(0)
            

def start_server(port, server_name, next_port, prev_port):
    """Start the server and initialize heartbeats."""
    global server_id, next_server_url, prev_server_url, current_port
    current_port = port
    server_id = server_name
    next_server_url = f"127.0.0.1:{next_port}"
    prev_server_url = f"127.0.0.1:{prev_port}"
    log("RESET",f"{server_id}: Starting server on port {port}, Next server: {next_server_url}, Previous server: {prev_server_url}")

    # Start the heartbeat thread
    if server_id == "server1":
        thread = threading.Thread(target=start_heartbeat, daemon=True)
        thread.start()

    threadexec = threading.Thread(target=start_execution, daemon=True)
    threadexec.start()
    # Start the Flask server
    app.run(host='0.0.0.0', port=port, debug=False, use_reloader=False)

if __name__ == '__main__':
    if len(sys.argv) != 5:
        print("Usage: python server.py <port> <server_name> <NEXT_PORT> <PREV_PORT>")
        sys.exit(1)

    port = int(sys.argv[1])
    server_name = sys.argv[2]
    next_port = int(sys.argv[3])
    prev_port = int(sys.argv[4])

    start_server(port, server_name, next_port, prev_port)