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
import time
from pathlib import Path
from typing import Any

import threading

from questions import (
    generate_mathematics_question,
    generate_roman_numerals_question,
    generate_usable_addresses_question,
    generate_network_broadcast_question,
    solve_mathematics_question,
    solve_roman_numerals_question,
    solve_usable_addresses_question,
    solve_network_broadcast_question
)

players = {}
players_lock = threading.Lock()
config = {}
current_correct_answer = None

import re

def validate_username(username):
    return bool(re.match(r'^[a-zA-Z0-9]+$', username))


# Most of these functions have no arguments.
# That is because the server scaffold is purely describing processes
# It would be convenient to provide an OOP scaffold for this,
# however, this would assume knowledge of the paradigm, and some
# students do not like using OOP in Python
# Therefore, just the function names will be provided

def add_player(client_socket, username):
    with players_lock:
        players[client_socket] = {
            "username": username,
            "score": 0,
            "answered": False,
            "disconnected": False
        }


def remove_player(client_socket):
    with players_lock:
        if client_socket in players:
            players[client_socket]["disconnected"] = True


def handle_player_answer(client_socket):
    global current_correct_answer

    try:
        client_socket.settimeout(config["question_seconds"])
        data = client_socket.recv(4096)

        if not data:
            remove_player(client_socket)
            return

        message = json.loads(data.decode('utf-8'))

        if message.get("message_type") == "BYE":
            remove_player(client_socket)
            return

        if message.get("message_type") == "ANSWER":
            player_answer = message["answer"]
            is_correct = (player_answer == current_correct_answer)

            # Mark as answered and update score
            with players_lock:
                if client_socket in players:
                    players[client_socket]["answered"] = True
                    if is_correct:
                        players[client_socket]["score"] += 1

            # Send RESULT
            if is_correct:
                feedback = config["correct_answer"]
            else:
                feedback = config["incorrect_answer"]

            feedback = feedback.format(
                answer=player_answer,
                correct_answer=current_correct_answer
            )

            result_msg = {
                "message_type": "RESULT",
                "correct": is_correct,
                "feedback": feedback
            }

            # Send only to this client
            json_string = json.dumps(result_msg) + "\n"
            client_socket.sendall(json_string.encode('utf-8'))

    except socket.timeout:
        # Player didn't answer in time
        with players_lock:
            if client_socket in players:
                players[client_socket]["answered"] = True
    except (socket.error, OSError, json.JSONDecodeError, KeyError):
        remove_player(client_socket)


def send_to_all_players(message_dict):
    json_string = json.dumps(message_dict) + "\n"
    message_bytes = json_string.encode('utf-8')

    with players_lock:
        for sock, data in players.items():
            if not data["disconnected"]:
                try:
                    sock.sendall(message_bytes)
                except (socket.error, OSError):
                    data["disconnected"] = True


def receive_answers():
    # Wait for the players to send their answers
    with players_lock:
        active_sockets = [sock for sock, data in players.items() if not data["disconnected"]]
        # Reset answered flags
        for data in players.values():
            data["answered"] = False

    # Create threads to handle each player's answer
    threads = []
    for sock in active_sockets:
        t = threading.Thread(target=handle_player_answer, args=(sock,))
        t.start()
        threads.append(t)

    # Wait for timeout or all answers
    start_time = time.time()
    while time.time() - start_time < config["question_seconds"]:
        with players_lock:
            active_players = [data for sock, data in players.items() if not data["disconnected"]]
            if all(data["answered"] for data in active_players):
                break
        time.sleep(0.1)

    # Properly join all threads with remaining timeout
    remaining_time = config["question_seconds"] - (time.time() - start_time)
    for t in threads:
        if remaining_time > 0:
            t.join(timeout=max(0.1, remaining_time))
        else:
            t.join(timeout=0.1)


def generate_leaderboard_state() -> str:
    # The 'state' for a LEADERBOARD message
    with players_lock:
        # Get active players only
        active_players = [
            (data["username"], data["score"])
            for sock, data in players.items()
            if not data["disconnected"]
        ]

    # Sort by score (descending), then username (ascending)
    active_players.sort(key=lambda x: (-x[1], x[0]))

    # Build leaderboard
    lines = []
    current_rank = 1
    prev_score = None

    for i, (username, score) in enumerate(active_players):
        if score != prev_score:
            current_rank = i + 1

        point_word = config["points_noun_singular"] if score == 1 else config["points_noun_plural"]
        lines.append(f"{current_rank}. {username}: {score} {point_word}")
        prev_score = score

    return "\n".join(lines)


def generate_question(question_type: str) -> dict[str, Any]:
    generators = {
        "Mathematics": generate_mathematics_question,
        "Roman Numerals": generate_roman_numerals_question,
        "Usable IP Addresses of a Subnet": generate_usable_addresses_question,
        "Network and Broadcast Address of a Subnet": generate_network_broadcast_question
    }

    generator = generators[question_type]
    short_question = generator()

    return {
        "short_question": short_question,
        "question_type": question_type
    }


def generate_question_answer(question_type: str, short_question: str) -> str:
    # You need this to check if the player's answer is correct
    # That will determine the 'feedback' in the RESULT message sent
    # The answer depends on the question type

    solvers = {
        "Mathematics": solve_mathematics_question,
        "Roman Numerals": solve_roman_numerals_question,
        "Usable IP Addresses of a Subnet": solve_usable_addresses_question,
        "Network and Broadcast Address of a Subnet": solve_network_broadcast_question
    }

    return solvers[question_type](short_question)

'''
def solve_mathematics_question(expression):

    tokens = expression.split()

    result = int(tokens[0])

    i = 1
    while i < len(tokens):
        operator = tokens[i]
        operand = int(tokens[i + 1])

        if operator == '+':
            result += operand
        elif operator == '-':
            result -= operand

        i += 2

    return str(result)


def solve_roman_numerals_question(roman):

    val = {
        'I': 1, 'V': 5, 'X': 10, 'L': 50,
        'C': 100, 'D': 500, 'M': 1000
    }

    total = 0
    prev_value = 0

    # Process right to left
    for char in reversed(roman):
        if char not in val:
            continue
        value = val[char]
        if value < prev_value:
            # Subtractive notation (like IV = 4)
            total -= value
        else:
            total += value
        prev_value = value

    return str(total)


def solve_usable_addresses_question(cidr):

    _, _, num_addresses = parse_cidr(cidr)
    # Usable addresses = total - 2 (network and broadcast)
    usable = num_addresses - 2
    return str(usable)

def solve_network_broadcast_question(cidr):

    network_addr, broadcast_addr, _ = parse_cidr(cidr)
    return f"{network_addr} and {broadcast_addr}"
'''



def parse_cidr(cidr):

    try:
        ip_str, prefix_str = cidr.split('/')
    except ValueError:
        print("Invalid cidr: " + cidr)
        return
    prefix_length = int(prefix_str)

    # Convert IP to integer
    ip_int = ip_to_int(ip_str)

    # Calculate subnet mask
    # For /24: 11111111.11111111.11111111.00000000 = 0xFFFFFF00
    mask = (0xFFFFFFFF << (32 - prefix_length)) & 0xFFFFFFFF

    # Calculate network address (IP AND mask)
    network_int = ip_int & mask

    # Calculate broadcast address (network OR inverted mask)
    broadcast_int = network_int | (~mask & 0xFFFFFFFF)

    # Total number of addresses in subnet
    num_addresses = 2 ** (32 - prefix_length)

    return (int_to_ip(network_int), int_to_ip(broadcast_int), num_addresses)

def ip_to_int(ip_str):
    """Convert IP address string to 32-bit integer."""
    octets = ip_str.split('.')
    return (int(octets[0]) << 24) + (int(octets[1]) << 16) + \
           (int(octets[2]) << 8) + int(octets[3])

def int_to_ip(ip_int):
    """Convert 32-bit integer to IP address string."""
    return f"{(ip_int >> 24) & 0xFF}.{(ip_int >> 16) & 0xFF}." \
           f"{(ip_int >> 8) & 0xFF}.{ip_int & 0xFF}"


def start_game():
    # Send a READY message

    ready_msg = {
        "message_type": "READY",
        "info": config["ready_info"].format(
            question_interval_seconds=config["question_interval_seconds"]
        )
    }
    send_to_all_players(ready_msg)
    time.sleep(config["question_interval_seconds"])


def start_round(question_number: int, question_type: str):
    # Here's where you'd send a question

    global current_correct_answer

    # Generate question
    question_data = generate_question(question_type)
    short_question = question_data["short_question"]

    # Get correct answer
    current_correct_answer = generate_question_answer(question_type, short_question)

    # Format question
    question_format = config["question_formats"][question_type]
    formatted_question = question_format.format(short_question)

    trivia_question = f"{config['question_word']} {question_number} ({question_type}):\n{formatted_question}"

    # Send QUESTION
    question_msg = {
        "message_type": "QUESTION",
        "question_type": question_type,
        "trivia_question": trivia_question,
        "short_question": short_question,
        "time_limit": config["question_seconds"]
    }
    send_to_all_players(question_msg)

    # Wait for answers
    receive_answers()


def end_round(is_last_round):
    # Here's where you'd either send LEADERBOARD or FINISHED

    if not is_last_round:
        # Send LEADERBOARD
        leaderboard_msg = {
            "message_type": "LEADERBOARD",
            "state": generate_leaderboard_state()
        }
        send_to_all_players(leaderboard_msg)
        time.sleep(config["question_interval_seconds"])
    else:
        # Send FINISHED
        state = generate_leaderboard_state()

        # Get winners
        with players_lock:
            active_players = [
                (data["username"], data["score"])
                for sock, data in players.items()
                if not data["disconnected"]
            ]

        active_players.sort(key=lambda x: (-x[1], x[0]))

        if active_players:
            max_score = active_players[0][1]
            winners = [name for name, score in active_players if score == max_score]

            if len(winners) == 1:
                winner_text = config["one_winner"].format(winners[0])
            else:
                winner_text = config["multiple_winners"].format(", ".join(sorted(winners)))
        else:
            winner_text = ""

        final_standings = f"{config['final_standings_heading']}\n{state}\n{winner_text}"

        finished_msg = {
            "message_type": "FINISHED",
            "final_standings": final_standings
        }
        send_to_all_players(finished_msg)


def main():

    global config

    #Load and validate the config
    if len(sys.argv) < 3:
        print("server.py: Configuration not provided", file=sys.stderr)
        sys.exit(1)
    else:
        if sys.argv[1] != "--config" and sys.argv[2] != "--config":
            print("server.py: Configuration not provided", file=sys.stderr)
            sys.exit(1)
    '''
    if len(sys.argv) < 3:
        print("server.py: Configuration not provided", file=sys.stderr)
        sys.exit(1)
    '''


    config_path = sys.argv[2]

    if not config_path.endswith(".json"):
        print("server.py: Configuration not provided", file=sys.stderr)

    if not Path(config_path).exists():
        print(f"server.py: File {config_path} does not exist", file=sys.stderr)
        sys.exit(1)

    #try to load the config
    try:
        with open(config_path) as f:
            config = json.load(f)
    except json.JSONDecodeError as e:
        print(f"server.py: Invalid JSON in config file", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"server.py: Error loading config: {e}", file=sys.stderr)
        sys.exit(1)

    # Validate config has required fields
    required_fields = [
        "port", "players", "question_types", "question_formats",
        "question_seconds", "question_interval_seconds", "ready_info",
        "question_word", "correct_answer", "incorrect_answer",
        "points_noun_singular", "points_noun_plural",
        "final_standings_heading", "one_winner", "multiple_winners"
    ]
    for field in required_fields:
        if field not in config:
            print(f"server.py: Missing required field '{field}' in config", file=sys.stderr)
            sys.exit(1)

    # start hosting
    # bind to port, listen for connections
    try:
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server_socket.bind(('0.0.0.0', config["port"]))
        server_socket.listen()
    except OSError:
        print(f"server.py: Binding to port {config['port']} was unsuccessful", file=sys.stderr)
        sys.exit(1)

    # Wait for players to join
    def handle_client_connection(client_sock):
        try:
            data = client_sock.recv(4096)
            if not data:
                client_sock.close()
                return

            message = json.loads(data.decode('utf-8'))
            if message.get("message_type") != "HI":
                client_sock.close()
                return

            username = message["username"]

            # Check alphanumeric
            if not validate_username(username):
                with players_lock:
                    for sock in list(players.keys()):
                        try:
                            sock.close()
                        except (socket.error, OSError):
                            pass
                sys.exit(0)

            add_player(client_sock, username)
        except (socket.error, OSError, json.JSONDecodeError, KeyError):
            client_sock.close()

    # Accept players
    threads = []
    for _ in range(config["players"]):
        client_sock, addr = server_socket.accept()
        t = threading.Thread(target=handle_client_connection, args=(client_sock,))
        t.start()
        threads.append(t)

    # Wait for all connection handler threads to finish
    for t in threads:
        t.join()

    start_game()

    # for each question type:
    # generate question
    # send question to all connected players
    # wait question_seconds OR for every player to answer
    # finish the round
    num_questions = len(config["question_types"])
    for i, question_type in enumerate(config["question_types"]):
        question_number = i + 1
        is_last = (i == num_questions - 1)
        start_round(question_number, question_type)
        end_round(is_last)
    # Close all connections
    with players_lock:
        for sock in list(players.keys()):
            try:
                sock.close()
            except (socket.error, OSError):
                pass

    server_socket.close()


if __name__ == "__main__":
    main()