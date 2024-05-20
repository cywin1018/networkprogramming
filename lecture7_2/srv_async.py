import select, zen_utils


# Page 9
def all_events_forever(poll_object):
    while True:
        for fd, event in poll_object.poll():
            yield fd, event


if __name__ == "__main__":
    address = zen_utils.parse_command_line("low-level async server")
    listener = zen_utils.create_srv_socket(address)
    serve(listener)
