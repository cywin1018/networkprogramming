import argparse, socket, time

# Page 6

aphorisms = {
    b"Beautiful is better than?": b"Ugly.",
    b"Explicit is better than?": b"Implicit.",
    b"Simple is better than?": b"Complex.",
}

# Page 7


def get_answer(aphorism):
    """Return the string response to a particular Zen-of-Python aphorism."""
    time.sleep(0.0)
    return aphorisms.get(aphorism, b"Error: unknown aphorism.")


# Page 8


def parse_command_line(description):
    """Parse the command line and return the address and port to use."""
    parser = argparse.ArgumentParser(description=description)
    parser.add_argument("host", help="IP or hostname")
    parser.add_argument(
        "-p", metavar="port", type=int, default=1060, help="TCP port (default 1060)"
    )
    args = parser.parse_args()
    address = (args.host, args.p)
    return address


# Page 9
def create_srv_socket(address):
    """Build and return a listening server socket."""
    listener = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    listener.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    listener.bind(address)
    listener.listen(64)
    print(f"Listening at {address}")
    return listener


# Page 10
def accept_connections_forever(listener):
    """Forever answer incoming connections on a listening socket."""
    while True:
        sock, address = listener.accept()
        print(f"Accepted connection from {address}")
        handle_conversation(sock, address)


# Page 11
def handle_conversation(sock, address):
    """Converse with a client over `sock` until they are done talking."""
    try:
        while True:
            handle_request(sock)
    except EOFError:
        print(f"Client socket to {address} has closed")
    except Exception as e:
        print(f"Client {address} error: {e}")
    finally:
        sock.close()


# Page 12
def handle_request(sock):
    """Receive a single client request on `sock` and send the answer."""
    aphorism = recv_until(sock, b"?")
    answer = get_answer(aphorism)
    sock.sendall(answer)


# Page 13
def recv_until(sock, suffix):
    """Receive bytes over socket `sock` until we receive the `suffix`."""
    message = sock.recv(4096)
    if not message:
        raise EOFError("socket closed")
    while not message.endswith(suffix):
        data = sock.recv(4096)
        if not data:
            raise IOError("received {!r} then socket closed".format(message))
        message += data
    return message

