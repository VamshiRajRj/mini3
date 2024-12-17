# import json
# import os
# import subprocess
# import time
# import requests

# def load_config(config_file):
#     """Load server configuration from the JSON file."""
#     with open(config_file, 'r') as file:
#         return json.load(file)["servers"]
    
# def get_script_path(script_name):
#     """Get the absolute path of a script located in the same directory."""
#     return os.path.join(os.path.dirname(os.path.abspath(__file__)), script_name)

# def start_servers(servers):
#     """Start servers in separate terminal windows."""
#     processes = []
#     server_script = get_script_path("server.py")

#     for server in servers:
#         port = server["port"]
#         name = server["name"]
#         next = server["next"]
#         prev = server["prev"]
#         command = f"python3 {server_script} {str(port)} {name} {str(next)} {str(prev)}"

#         print(f"Starting {name} on port {port}...")
#         if os.name == "nt":  # Windows
#             processes.append(subprocess.Popen(["start", "cmd", "/k"] + command, shell=True))
#         elif os.name == "posix":  # macOS/Linux
#             subprocess.Popen([
#                 "osascript", "-e",
#                 f'tell application "Terminal" to do script "{command}"'
#             ])
#         time.sleep(1)  # Wait briefly to ensure the server starts

#     return processes

# # def setup_ring(servers):
# #     """Set up the circular linked list by linking servers."""
# #     for i in range(len(servers)):
# #         current_server = servers[i]

# #         prev_url = f"127.0.0.1:{current_server['prev']}"
# #         current_url = f"127.0.0.1:{current_server['port']}"
# #         next_url = f"127.0.0.1:{current_server['next']}"

# #         print(f"Linking {current_server['prev']} ({prev_url}) → {current_server['name']} ({current_url}) → {current_server['next']} ({next_url})")
# #         try:
# #             requests.post(f"http://{current_url}/set_next", json={"next_server_url": next_url}, timeout=5)
# #         except Exception as e:
# #             print(f"[ERROR] Failed to link {current_server['name']} to {next_server['name']}: {e}")

# if __name__ == "__main__":
#     config_file = "config.json"
#     servers = load_config(config_file)

#     print("[INFO] Starting servers...")
#     processes = start_servers(servers)

#     print("[INFO] Setting up the circular ring topology...")
#     time.sleep(3)  # Allow servers to start
#     # setup_ring(servers)

#     print("[INFO] Servers are running and linked in a circular topology.")
#     print("[INFO] Press Ctrl+C to stop.")

import json
import os
import subprocess
import time
import requests
import sys

def load_config(config_file):
    """Load server configuration from the JSON file."""
    with open(config_file, 'r') as file:
        return json.load(file)["servers"]

def create_virtualenv(venv_dir, script_dir):
    """Create a virtual environment in the server.py directory."""
    os.chdir(script_dir)  # Change to the server directory
    if not os.path.exists(venv_dir):
        print(f"[INFO] Creating virtual environment in {venv_dir}...")
        subprocess.run([sys.executable, "-m", "venv", venv_dir], check=True)
    else:
        print(f"[INFO] Virtual environment already exists in {venv_dir}.")

    # Install dependencies
    pip_path = os.path.join(venv_dir, "bin", "pip" if os.name != "nt" else "Scripts\\pip.exe")
    print("[INFO] Installing dependencies...")
    subprocess.run([pip_path, "install", "-r", "requirements.txt"], check=True)

def get_script_path(script_name):
    """Get the absolute path of a script located in the same directory."""
    return os.path.join(os.path.dirname(os.path.abspath(__file__)), script_name)

def start_servers(servers, venv_dir, server_script):
    """Start servers in separate terminal windows using venv's Python."""
    

    for server in servers:
        port = server["port"]
        name = server["name"]
        command = f"{python_path} {server_script} {port} {name}"

        print(f"Starting {name} on port {port}...")
        if os.name == "posix":  # macOS/Linux
            subprocess.Popen([
                "osascript", "-e",
                f'tell application "Terminal" to do script "{command}"'
            ])
        elif os.name == "nt":  # Windows
            subprocess.Popen(["start", "cmd", "/k", command], shell=True)
        else:
            print(f"[ERROR] Unsupported OS: {os.name}")
        time.sleep(1)

def start_servers(servers, venv_dir, server_script):
    """Start servers in separate terminal windows."""
    processes = []
    python_path = os.path.join(venv_dir, "bin", "python3" if os.name != "nt" else "Scripts\\python.exe")

    for server in servers:
        port = server["port"]
        name = server["name"]
        next = server["next"]
        prev = server["prev"]
        command = f"{python_path} {server_script} {str(port)} {name} {str(next)} {str(prev)}"

        print(f"Starting {name} on port {port}...")
        if os.name == "nt":  # Windows
            processes.append(subprocess.Popen(["start", "cmd", "/k"] + command, shell=True))
        elif os.name == "posix":  # macOS/Linux
            subprocess.Popen([
                "osascript", "-e",
                f'tell application "Terminal" to do script "{command}"'
            ])
        time.sleep(1)  # Wait briefly to ensure the server starts

    return processes

def setup_ring(servers):
    """Set up the circular linked list by linking servers."""
    for i in range(len(servers)):
        current_server = servers[i]
        next_server = servers[(i + 1) % len(servers)]  # Circular link

        current_url = f"127.0.0.1:{current_server['port']}"
        next_url = f"127.0.0.1:{next_server['port']}"

        print(f"Linking {current_server['name']} ({current_url}) → {next_server['name']} ({next_url})")
        try:
            requests.post(f"http://{current_url}/set_next", json={"next_server_url": next_url}, timeout=5)
        except Exception as e:
            print(f"[ERROR] Failed to link {current_server['name']} to {next_server['name']}: {e}")

if __name__ == "__main__":
    # Paths
    script_dir = os.path.dirname(os.path.abspath(__file__))  # Directory containing server.py
    config_file = os.path.join(script_dir, "config.json")
    server_script = os.path.join(script_dir, "server.py")
    venv_dir = os.path.join(script_dir, "venv")

    # Load server configuration
    servers = load_config(config_file)

    # Create virtual environment in server.py directory
    print("[INFO] Setting up virtual environment and dependencies...")
    create_virtualenv(venv_dir, script_dir)

    # Start servers using venv's Python
    print("[INFO] Starting servers...")
    start_servers(servers, venv_dir, server_script)

    # Set up circular ring topology
    print("[INFO] Setting up the circular ring topology...")
    time.sleep(3)  # Allow servers to start
    setup_ring(servers)

    print("[INFO] Servers are running and linked in a circular topology.")
    print("[INFO] Press Ctrl+C to stop.")