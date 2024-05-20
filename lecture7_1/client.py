import argparse, socket, random, zen_utils


# Page 14
def client(address, cause_error=False):
    """Connect to a server at `address` and send it some data."""
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect(address)
    aphorisms = list(zen_utils.aphorisms)
    if cause_error:
        sock.sendall(aphorisms[0][:-1])
        return
    for aphorism in random.sample(aphorisms, 3):
        sock.sendall(aphorism)
        print(aphorism, zen_utils.recv_until(sock, b"."))
    sock.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Example client")
    parser.add_argument("host", help="IP or hostname")
    parser.add_argument("-e", help="store_true", help="cause an error")
    parser.add_argument("-p", type=int, help="TCP port (default 1060)", default=1060)
    parser.add_argument(
        "--cause-error", action="store_true", help="Cause an error in the server"
    )
    args = parser.parse_args()
    address = zen_utils.get_address(args.host, args.port)
    client(address, args.e)
