import zen_utils
from threading import Thread
import multiprocessing as mp


def start_threads(listener, workers=4):
    t = (listener,)
    for i in range(workers):
        th = Thread(target=zen_utils.accept_connections_forever, args=t)
        th.start()


def start_processes(listener, workers=4):
    t = (listener,)
    for i in range(workers):
        p = mp.Process(target=zen_utils.accept_connections_forever, args=t)
        p.start()


if __name__ == '__main__':
    address = zen_utils.parse_command_line('multi-threaded server')
    listener = zen_utils.create_srv_socket(address)
    # start_threads(listener)
    start_processes(listener)
