import zen_utils

if __name__ == "__main__":
    address = zen_utils.parse_command_line('simple single-threaded server')
    listener = zen_utils.create_srv_socket(address)
    zen_utils.accept_connections_forever(listener)


# Page 26
# 멀티 스레드 : 여러 스레드가 동일 메모리 자원을 공유
# 멀티 프로세싱 : 여러 프로세스가 각각의 메모리 자원을 가짐.
# CPU 바운드 작업에는 멀티프로세싱이, I/O 바운드 작업에는 멀티스레딩이 적합할 수 있습니다.

