import requests

def send_request(server_url, tasks):
    """Send a key-value pair to the specified server."""
    try:
        response = requests.post(f"http://localhost:{server_url}/process", json={"tasks": tasks, "client_url": "value"})
        print(response.json())
    except requests.exceptions.RequestException as e:
        print(f"Error sending request: {e}")

def get_processed_data(server_url):
    """Retrieve all processed key-value pairs from a server."""
    try:
        response = requests.get(f"http://localhost:{server_url}/processed")
        print("Processed data:", response.json())
    except requests.exceptions.RequestException as e:
        print(f"Error retrieving processed data: {e}")

if __name__ == '__main__':
    
    

    while True:
        print("Enter the server URL to interact with (8080 or 8081 or 8082 or 8083):")
        server_url = input("Server PORT: ")
        print("\nChoose an action:")
        print("1. Enter the tasks")
        print("3. Exit")

        choice = input("Enter your choice: ")
        if choice == "1":
            tasks = input("Enter space seperated numbers: ").split()
            send_request(server_url, tasks)
        elif choice == "3":
            print("Exiting...")
            break
        else:
            print("Invalid choice. Please try again.")