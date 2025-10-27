# THIS IS JUST A SCAFFOLD
# Change anything you like about it!
# It just provides some guidelines on where to start
# There are a lot of things missing, and many function
# signatures, names and types used
# can and should be adjusted for your convenience
# This is not necessarily code with good structure or layout
# and the functions do not cover everything
# Use it as you wish.


import json
import socket
import sys
import threading
import select
import requests

from pathlib import Path
from typing import Any, Literal

from questions import *

config = {}
client_socket = None
connected: bool = False
current_time_limit: int = 0
current_question_type = None


def encode_message(message: dict[str, Any]) -> bytes:
    # encode data with newline delimiter
    return (json.dumps(message) + '\n').encode('utf-8')


def decode_message(message: bytes) -> dict[str, Any]:
    # decode message received from server
    return json.loads(message.decode('utf-8').strip())


def send_message(client_socket, data: dict[str, Any]):
    # Use encode_message
    # Send data across the socket
    client_socket.sendall(encode_message(data))


def receive_message(socket_socket) -> dict[str, Any] | None:
    # Use decode_message
    # Receive data from the socket, and
    # return the data decoded
    data = b""
    while True:
        chunk = socket_socket.recv(1)
        if not chunk:
            return None
        data += chunk
        if chunk == b'\n':
            break

    if not data.strip():
        return None

    return decode_message(data)


def connect(hostname: str, port: int) -> socket.socket:
    # Connect to the server socket
    # Then, send your HI message!
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect((hostname, port))
        return sock
    except Exception:
        print("Connection failed")
        sys.exit(0)


def disconnect(client_socket):
    # Disconnect from the server socket
    # Then, send your BYE message!
    try:
        bye_msg = {"message_type": "BYE"}
        client_socket.sendall(encode_message(bye_msg))
    except (socket.error, OSError):
        pass
    client_socket.close()


def answer_question(
        question: str,
        short_question: str,
        client_mode: Literal["you", "auto", "ai"]) -> str:
    global current_time_limit, current_question_type

    if client_mode == "you":
        try:
            ready, _, _ = select.select([sys.stdin], [], [], current_time_limit)

            if ready:
                answer = sys.stdin.readline().strip()
                return answer
            else:
                return ""
        except Exception:
            return ""


    elif client_mode == "auto":
        # Automatically answer the question
        try:
            return solve_question_auto(current_question_type, short_question)
        except Exception:
            return ""


    elif client_mode == "ai":
        # Use Ollama
        return answer_question_ollama(question)

    return ""


def solve_question_auto(question_type: str, short_question: str) -> str:
    # helper function to solve questions in auto mode

    solvers = {
        "Mathematics": solve_mathematics_question,
        "Roman Numerals": solve_roman_numerals_question,
        "Usable IP Addresses of a Subnet": solve_usable_ip_addresses_question,
        "Network and Broadcast Address of a Subnet": solve_network_broadcast_question
    }

    return solvers[question_type](short_question)

def answer_question_ollama(question: str) -> str:
    # Use requests here!
    """
        Use requests to get answer from Ollama.

        This function sends the question to Ollama's /api/chat endpoint
        and returns the AI-generated answer.

        Args:
            question: The full trivia question text

        Returns:
            The answer as a string, or empty string if error/timeout
        """
    global config, current_time_limit

    try:
        # Get Ollama configuration
        ollama_config = config["ollama_config"]
        url = f"http://{ollama_config['ollama_host']}:{ollama_config['ollama_port']}/api/chat"

        # Prepare the request payload
        payload = {
            "model": ollama_config["ollama_model"],
            "messages": [
                {
                    "role": "user",
                    "content": f"Answer this trivia question with just the answer, no explanation: {question}"
                }
            ],
            "stream": False  # Don't stream, get complete response
        }

        # Send POST request to Ollama with timeout
        response = requests.post(url, json=payload, timeout=current_time_limit)

        # Check if request was successful
        if response.status_code != 200:
            return ""

        # Parse JSON response
        result = response.json()

        # Extract answer from response
        # Ollama returns: {"message": {"content": "answer here"}}
        answer = result["message"]["content"].strip()

        return answer

    except requests.exceptions.Timeout:
        # Ollama took too long to respond
        return ""
    except requests.exceptions.ConnectionError:
        # Ollama is not running or unreachable
        return ""
    except (KeyError, json.JSONDecodeError):
        # Response format is unexpected
        return ""
    except Exception:
        # Any other error
        return ""


def handle_command(command: str):
    # Handle behaviour for sending the following messages:
    # CONNECT <host>:<port>
    # DISCONNECT
    # EXIT

    global client_socket, ConnectionAbortedError, connected

    if command == "EXIT":
        if connected and client_socket:
            disconnect(client_socket)
        sys.exit(0)

    elif command.startswith("CONNECT "):
        if not connected:
            parts = command.split()
            if len(parts) == 2:
                host_port = parts[1].split(':')
                if len(host_port) == 2:
                    hostname = host_port[0]
                    port = int(host_port[1])

                    client_socket = connect(hostname, port)
                    connected = True

                    # Send HI message immediately after connecting
                    hi_msg = {
                        "message_type": "HI",
                        "username": config["username"]
                    }
                    send_message(client_socket, hi_msg)

                    # then start server message handler threading
                    server_thread = threading.Thread(target=handle_server_messages, daemon=True)
                    server_thread.start()

    elif command == "DISCONNECT":
        if connected and client_socket:
            disconnect(client_socket)
            sys.exit(0)


def handle_received_message(message: dict[str, Any]):
    # Messages you have to handle (only while connected to a server):
    # READY
    # QUESTION
    # RESULT
    # LEADERBOARD
    # FINISHED

    global client_socket, connected, current_time_limit, current_question_type, config

    msg_type = message.get("message_type")

    if msg_type == "READY":
        print(message["info"])

    elif msg_type == "QUESTION":
        print(message["trivia_question"])

        # Store time limit and question type for answer function
        current_time_limit = message["time_limit"]
        current_question_type = message["question_type"]

        # Get answer using answer_question function
        answer = answer_question(
            question=message["trivia_question"],
            short_question=message["short_question"],
            client_mode=config["client_mode"]
        )

        # Send answer if we got one (not empty due to timeout)
        if answer:
            answer_msg = {
                "message_type": "ANSWER",
                "answer": answer
            }
            send_message(client_socket, answer_msg)

    elif msg_type == "RESULT":
        print(message["feedback"])

    elif msg_type == "LEADERBOARD":
        print(message["state"])

    elif msg_type == "FINISHED":
        print(message["final_standings"])
        connected = False
        client_socket.close()
        sys.exit(0)


def handle_server_messages():
    # handle incoming messages from server in a separate threading

    global client_socket, connected

    try:
        while connected:
            message = receive_message(client_socket)

            if not message:
                connected = False
                client_socket.close()
                sys.exit(0)

            handle_received_message(message)

    except Exception:
        if connected:
            client_socket.close()
        sys.exit(0)


def main():
    # The client consists of few parts compared to the server:
    # Parsing and loading config files
    # Connecting, disconnecting and exiting
    # Responding to normal messages (CONNECT, DISCONNECT, EXIT)
    # Responding to server messages (READY, QUESTION, RESULT, LEADERBOARD, FINISHED)
    # Answer questions depending on the mode ('you', 'auto' or 'ai')

    global config

    # parse arguments from sys.argv
    if len(sys.argv) < 2:
        print("client.py: Configuration not provided", file=sys.stderr)
        sys.exit(1)
    elif sys.argv[1] == "--config":
        if len(sys.argv) < 3:
            print("client.py: Configuration not provided", file=sys.stderr)
            sys.exit(1)
        config_path = sys.argv[2]
    else:
        print("client.py: Configuration not provided", file=sys.stderr)
        sys.exit(1)

    # load Configuration
    if not Path(config_path).exists():
        print(f"client.py: File {config_path} does not exist", file=sys.stderr)
        sys.exit(1)

    with open(config_path) as f:
        config = json.load(f)

    # check Ollama config
    if config.get("client_mode") == 'ai':
        if not config.get("ollama_config"):
            print("client.py: Missing values for Ollama configuration", file=sys.stderr)
            sys.exit(1)

    # handle user input

    try:
        while True:
            user_input = input()
            handle_command(user_input)
    except (EOFError, KeyboardInterrupt):
        if connected and client_socket:
            disconnect(client_socket)
        sys.exit(0)


if __name__ == "__main__":
    main()