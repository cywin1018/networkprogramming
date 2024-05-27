import socket
import ssl
import json
import logging
import zmq
import threading
import random

# Configure logging settings
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Define ports for multi-player mode
MULTI_PORT_PUB = 56661
MULTI_PORT_REP = 56662

# Function to generate a unique client ID
def generate_client_id():
    return str(random.randint(1000, 9999))

# Function to handle the initial interaction with the server to choose a game mode
def start(ssl_sock, client_id):
    """
    Handles the initial interaction with the server to choose a game mode.
    """
    while True:
        print("===============================")
        print("Choose game mode")
        print("Enter : '1' to play single mode")
        print("Enter : '2' to play multi mode")
        print("Enter : 'exit' to leave..")
        print("===============================")
        input_to_start = input()
        if input_to_start in ["1", "2", "exit"]:
            break
        else:
            logger.error("Please enter '1' or '2' or 'exit'.")

    # Send the chosen mode to the server
    message = {'choose_mode': input_to_start, 'client_id': client_id}
    json_message = json.dumps(message)
    try:
        ssl_sock.sendall(json_message.encode())
        server_response = ssl_sock.recv(1024).decode()
        decoded_response = json.loads(server_response)
        if 'choose_mode' in decoded_response:
            if 'message' in decoded_response:
                print(decoded_response['message'])
            return decoded_response['choose_mode']
    except (ssl.SSLError, json.JSONDecodeError, socket.error) as e:
        logger.error(f"An error occurred during start: {e}")
        return None

    # Graceful closing process
    if input_to_start == "exit":
        ssl_sock.close()
        return input_to_start

# Function to handle the single player mode of the game
def single_mode(ssl_sock, client_id):
    """
    Handles the single player mode of the game.
    """
    print("---- 'Guess the number' game start! ----")
    while True:
        print("Guess a number between 1 to 10 or type 'exit' to leave:")
        guess = input()
        if guess == 'exit':
            # Send exit message to the server
            message = {'exit': True, 'client_id': client_id}
            json_message = json.dumps(message)
            ssl_sock.sendall(json_message.encode())
            return 0
        if guess.isdigit():
            guess = int(guess)
            if guess < 1 or guess > 10:
                logger.error("Enter an integer number between 1 to 10 or type 'exit' to leave.")
                continue
        else:
            logger.error("Enter an integer number between 1 to 10 or type 'exit' to leave.")
            continue

        # Send the guessed number to the server
        message = {'guess': guess, 'client_id': client_id}
        json_message = json.dumps(message)
        try:
            ssl_sock.sendall(json_message.encode())
            response = ssl_sock.recv(1024).decode()
            result = json.loads(response)
            if 'result' in result:
                print(result['result'])
                if result['result'] == "Congratulations, you did it." or result['result'] == "Sorry, you've used all your attempts!":
                    return 1
        except (ssl.SSLError, json.JSONDecodeError, socket.error) as e:
            logger.error(f"An error occurred during game: {e}")
            return -1

# Function to ask the player if they want to play again after a game ends
def again(ssl_sock, client_id):
    """
    Asks the player if they want to play again after a game ends.
    """
    while True:
        print("===============================")
        print("Enter 'yes' to play again or 'exit' to leave the game:")
        print("===============================")
        input_to_again = input()
        if input_to_again in ["yes", "exit"]:
            # Send the play again choice to the server
            message = {'do_again': input_to_again, 'client_id': client_id}
            json_message = json.dumps(message)
            try:
                ssl_sock.sendall(json_message.encode())
                server_response = ssl_sock.recv(1024).decode()
                decoded_response = json.loads(server_response)
                if 'do_again' in decoded_response:
                    return decoded_response['do_again']
            except (ssl.SSLError, json.JSONDecodeError, socket.error) as e:
                logger.error(f"An error occurred during again: {e}")
                return 'exit'
        else:
            logger.error("Please enter 'yes' or 'exit'.")

# Function to handle the multi-player mode of the game
def multi_mode(client_id):
    """
    Handles the multi-player mode of the game.
    """
    context = zmq.Context()

    # REQ socket for sending guesses to the server
    socket_req = context.socket(zmq.REQ)
    socket_req.connect(f"tcp://localhost:{MULTI_PORT_REP}")

    # SUB socket for receiving hints and results from the server
    socket_sub = context.socket(zmq.SUB)
    socket_sub.connect(f"tcp://localhost:{MULTI_PORT_PUB}")
    socket_sub.setsockopt_string(zmq.SUBSCRIBE, '')

    stop_event = threading.Event()

    # Thread function to receive messages from the server
    def receive_messages():
        """
        Thread function to receive messages from the server.
        """
        while not stop_event.is_set():
            try:
                message = socket_sub.recv_json(flags=zmq.NOBLOCK)
                if 'result' in message:
                    print(message['result'])
                if message.get('game_over'):
                    stop_event.set()  # Signal the main thread to stop
            except zmq.Again:
                pass

    # Start the message receiving thread
    thread = threading.Thread(target=receive_messages, daemon=True)
    thread.start()

    while True:
        print("Guess a number between 1 to 10 or type 'exit' to leave:")
        guess = input()
        if guess == 'exit':
            socket_req.send_json({'exit': True, 'client_id': client_id})
            response = socket_req.recv_json()
            break
        if guess.isdigit():
            guess = int(guess)
            if guess < 1 or guess > 10:
                print("Enter an integer number between 1 to 10.")
                continue
        else:
            print("Enter an integer number.")
            continue

        # Send the guessed number to the server
        socket_req.send_json({'guess': guess, 'client_id': client_id})
        socket_req.recv_json()

    stop_event.set()  # Signal the receiving thread to stop
    # Wait for the receiving thread to finish
    thread.join()

    # Properly close the sockets
    socket_req.close()
    socket_sub.close()
    context.term()

# Main client function to handle connection and game modes
def guess_the_name_client():
    """
    Main client function to handle connection and game modes.
    """
    server_ip = '127.0.0.1'
    server_port = 56660

    context = ssl.create_default_context(purpose=ssl.Purpose.SERVER_AUTH, cafile='cert.crt')

    # Generate a unique client ID
    client_id = generate_client_id()
    print(f"*************** Your client (ID: {client_id}) ***************")

    # Function to establish an SSL connection to the server
    def connect_to_server():
        """
        Establishes an SSL connection to the server.
        """
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        client_socket.connect((server_ip, server_port))
        ssl_sock = context.wrap_socket(client_socket, server_hostname='Gwanrok')
        return ssl_sock

    try:
        ssl_sock = connect_to_server()
        while True:
            mode = start(ssl_sock, client_id)
            if mode == "exit":
                break
            if mode == "1":
                while True:
                    result = single_mode(ssl_sock, client_id)
                    if result == 0:
                        break
                    if result == 1:
                        play_again = again(ssl_sock, client_id)
                        if play_again == "exit":
                            break
            elif mode == "2":
                multi_mode(client_id)
                # Close the current SSL socket after multi_mode
                ssl_sock.close()
                # Reconnect to the server
                ssl_sock = connect_to_server()

    except Exception as e:
        logger.error(f"An unexpected error occurred: {e}")
    finally:
        ssl_sock.close()

# Entry point of the script
if __name__ == "__main__":
    guess_the_name_client()
