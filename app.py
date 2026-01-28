from app.app import app
import socket, sys

HOST = "127.0.0.1"
PORTS = (5000, 5001, 8000, 8080)

def find_port():
    for p in PORTS:
        with socket.socket() as s:
            s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            if s.connect_ex((HOST, p)) != 0:
                return p
    sys.exit(1)

app.run(host=HOST, port=find_port(), debug=True)
