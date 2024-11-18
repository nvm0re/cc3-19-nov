import argparse
import numpy as np
from sklearn.linear_model import LinearRegression
from pythonosc.dispatcher import Dispatcher
from pythonosc.osc_server import BlockingOSCUDPServer
from pythonosc.udp_client import SimpleUDPClient
from typing import List, Any

# Argument Parsing
parser = argparse.ArgumentParser(description="OSC Linear Regression Server")
parser.add_argument("--server-ip", type=str, default="127.0.0.1", help="IP address of the OSC server.")
parser.add_argument("--server-port", type=int, default=6448, help="Port number of the OSC server.")
parser.add_argument("--client-ip", timype=str, default="127.0.0.1", help="IP address of the OSC client.")
parser.add_argument("--client-port", type=int, default=12000, help="Port number of the OSC client.")
args = parser.parse_args()

# Global variables
inputs = 3
X = np.array([])
y = np.array([])
training = True

dispatcher = Dispatcher()
reg = LinearRegression()

def add_example(address: str, *args: List[Any]) -> None:
    global X, y, reg, training

    if training:
        Xadd = args[:inputs]
        yadd = args[inputs:]
        print(f"Received input: {Xadd} with output {yadd}")

        if X.size:
            X, y = np.vstack([X, Xadd]), np.vstack([y, yadd])
        else:
            X, y = np.array(Xadd), np.array(yadd)
    else:
        Xrun = args[:inputs]
        print("out: ", reg.predict(np.array([Xrun])))
        outList = reg.predict(np.array([Xrun]))[0]
        client.send_message("/outputs", outList)

def train(address: str, *args: List[Any]) -> None:
    global X, y, reg

    reg.fit(X, y)
    print("trained. score: ", reg.score(X, y))

def run(address: str, *args: List[Any]) -> None:
    global training
    training = not training

dispatcher.map("/inputs", add_example)
dispatcher.map("/train", train)
dispatcher.map("/run", run)

# Set up server and client with user-specified IP and port
server = BlockingOSCUDPServer((args.server_ip, args.server_port), dispatcher)
client = SimpleUDPClient(args.client_ip, args.client_port)

print(f"Starting OSC server at {args.server_ip}:{args.server_port}")
print(f"Client sending messages to {args.client_ip}:{args.client_port}")

server.serve_forever()
