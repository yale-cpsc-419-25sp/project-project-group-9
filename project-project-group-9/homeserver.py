import socket
import pickle

class HomeServer:
    def __init__(self, host='localhost', port=12345):
        self.host = host
        self.port = port
        self.users = {"admin": "password123", "user": "1234"}  # Sample user database

    def handle_request(self, data):
        page = pickle.loads(data)
        if page == "Take the Quiz!":
            return pickle.dumps("Login Page Loaded")
        return pickle.dumps(f"Page: {page} Loaded")

    def run(self):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server:
            server.bind((self.host, self.port))
            server.listen(5)
            print(f"Server running on {self.host}:{self.port}")
            while True:
                client, addr = server.accept()
                with client:
                    print(f"Connection from {addr}")
                    data = client.recv(4096)
                    if not data:
                        continue
                    response = self.handle_request(data)
                    client.sendall(response)

if __name__ == "__main__":
    server = HomeServer()
    server.run()

