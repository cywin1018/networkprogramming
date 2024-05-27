import json
import socket
import random
import ssl
import logging
import threading
import zmq

# Configure logging settings
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

MAX_ATTEMPTS = 5
MULTI_PORT_PUB = 56661
MULTI_PORT_REP = 56662

# Function to start a new game by generating a random number between 1 and 10
def start_game():
    """
    Generates a random number between 1 and 10 for the game.
    """
    return random.randint(1, 10)

# Function to handle multi-player mode using ZeroMQ for communication
def multi_mode_handler(socket_pub, socket_rep):
    """
    Handles the multi-player mode of the game using ZeroMQ for communication.
    """
    x = start_game()  # Generate the number to guess
    attempt = 0

    while True:
        message = socket_rep.recv_json()
        client_id = message.get('client_id')  # Unique client ID
        if 'exit' in message:
            logger.info(f"Client (id:{client_id}) exited the multi mode.")
            socket_rep.send_json({'status': 'exited'})
            continue
        elif 'guess' in message:
            guess = message['guess']
            attempt += 1
            if guess == x:
                response = {'result': f'Congratulations, Client (id:{client_id}) guessed it right!'}
                socket_pub.send_json(response)
                x = start_game()  # Start a new game
                attempt = 0
                socket_pub.send_json({'result': 'A new number has been chosen. Start guessing!'})
            elif guess < x:
                response = {'result': f'Hint: guessed number {guess} is too small!\n(The remaining opportunity : {MAX_ATTEMPTS-attempt})'}
                socket_pub.send_json(response)
            else:
                response = {'result': f'Hint: guessed {guess} is too high!\n(The remaining opportunity : {MAX_ATTEMPTS-attempt})'}
                socket_pub.send_json(response)

            if attempt >= MAX_ATTEMPTS and guess != x:
                response = {'result': 'Sorry, no one guessed it right. A new number has been set.'}
                socket_pub.send_json(response)
                x = start_game()  # Start a new game
                attempt = 0

            socket_rep.send_json({'status': 'received'})

# Function to initialize sockets and start the multi-player mode handler
def multi_mode():
    """
    Initializes the sockets and starts the multi-player mode handler.
    """
    context = zmq.Context()

    # PUB socket for broadcasting messages to all clients
    socket_pub = context.socket(zmq.PUB)
    socket_pub.bind(f"tcp://*:{MULTI_PORT_PUB}")

    # REP socket for receiving guesses from clients
    socket_rep = context.socket(zmq.REP)
    socket_rep.bind(f"tcp://*:{MULTI_PORT_REP}")

    try:
        multi_mode_handler(socket_pub, socket_rep)
    finally:
        socket_pub.close()
        socket_rep.close()
        context.term()

# Function to handle the single-player mode of the game
def single_mode(ssl_sock, client_id):
    """
    Handles the single-player mode of the game.
    """
    x = start_game()
    attempts = 1
    while True:
        try:
            data_in_main = ssl_sock.recv(1024)
            guess_value = json.loads(data_in_main.decode())
        except json.JSONDecodeError as e:
            logger.error(f"Error decoding JSON: {e}")
            return -1

        if 'exit' in guess_value:
            logger.info(f"Client (id:{client_id}) chose to exit the single_mode.")
            return 0

        if 'guess' in guess_value:
            guess = int(guess_value['guess'])
        if attempts <= MAX_ATTEMPTS:
            if guess == x:
                ssl_sock.sendall(json.dumps({'result': 'Congratulations, you did it.'}).encode())
                return 1
            elif guess < x:
                ssl_sock.sendall(json.dumps({'result': 'Hint: You guessed too small!'}).encode())
            else:
                ssl_sock.sendall(json.dumps({'result': 'Hint: You guessed too high!'}).encode())
            attempts += 1
        else:
            ssl_sock.sendall(json.dumps({'result': "Sorry, you've used all your attempts!"}).encode())
            return 1

# Function to handle the interaction with a connected client
def handle_client(ssl_sock, addr):
    """
    Handles the interaction with a connected client.
    """
    try:
        while True:
            data = ssl_sock.recv(1024)
            if not data:
                break
            message = json.loads(data.decode())

            client_id = message.get('client_id')
            if 'choose_mode' in message:
                if message['choose_mode'] == "1":
                    logger.info(f"Client (id:{client_id}) join the single_mode.")
                    single_mode_message = (
                        "*****************************************************\n"
                        "You have joined the single mode.\n"
                        "You have 5 attempts per game to guess the correct number between 1 and 10.\n"
                        "To exit the game at any time, type 'exit'.\n"
                        "*****************************************************\n"
                    )
                    ssl_sock.sendall(json.dumps({
                        'choose_mode': '1',
                        'message': single_mode_message
                    }).encode())
                    while True:
                        single_result = single_mode(ssl_sock, client_id)
                        if single_result != 1:
                            break
                        do_again = ssl_sock.recv(1024)
                        try_again = json.loads(do_again.decode())
                        if 'do_again' in try_again and try_again['do_again'].lower() == 'yes':
                            ssl_sock.send(json.dumps({'do_again': 'yes'}).encode())
                            continue
                        elif 'do_again' in try_again and try_again['do_again'].lower() == 'exit':
                            logger.info(f"Client (id:{client_id}) chose to exit the single_mode.")
                            ssl_sock.send(json.dumps({'do_again': 'exit'}).encode())
                            break

                elif message['choose_mode'] == "2":
                    logger.info(f"Client (id:{client_id}) join the multi_mode.")
                    multi_mode_message = (
                        "*****************************************************\n"
                        "You have joined the multi-mode.\n"
                        "You have 5 attempts per game to guess the correct number between 1 and 10.\n"
                        "All attempts are shared among all participants, and hint information about the guessed values will be provided.\n"
                        "To exit the multi-mode, type 'exit'.\n"
                        "*****************************************************\n"
                    )
                    ssl_sock.sendall(json.dumps({
                        'choose_mode': '2',
                        'message': multi_mode_message
                    }).encode())
                    multi_mode()

                elif message['choose_mode'] == "exit":
                    ssl_sock.sendall(json.dumps({'choose_mode': 'exit'}).encode())
                    break
    except Exception as e:
        pass
    finally:
        ssl_sock.close()

# Main server function to accept client connections and spawn handler threads
def server():
    """
    Main server function to accept client connections and spawn handler threads.
    """
    purpose = ssl.Purpose.CLIENT_AUTH
    context = ssl.create_default_context(purpose, cafile='cert.crt')
    context.load_cert_chain('key.pem')

    server_ip = '127.0.0.1'
    server_port = 56660

    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind((server_ip, server_port))
    server_socket.listen(5)
    logger.info(f"Server listening on {server_ip}:{server_port}")

    try:
        while True:
            client_socket, addr = server_socket.accept()
            ssl_sock = context.wrap_socket(client_socket, server_side=True)
            threading.Thread(target=handle_client, args=(ssl_sock, addr)).start()
    except Exception as e:
        logger.error(f"An error occurred: {e}")
    finally:
        server_socket.close()

if __name__ == "__main__":
    server()
