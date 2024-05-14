import asyncio
import zen_utils

@asyncio.coroutine
def handle_conversation(reader, writer):
    address = writer.get_extra_info('peername')
    print('Connection from {}'.format(address))
    try:
        while True:
            data = b''
            while not data.endswith(b'?'):
                more_data = yield from reader.read(4096)
                if not more_data:
                    if data:
                        print('Client {} sent {!r} but then closed'.format(address, data))
                    else:
                        print('Client {} closed socket normally'.format(address))
                    return
                data += more_data
            answer = zen_utils.get_answer(data)
            writer.write(answer)
            yield from writer.drain()
    except asyncio.CancelledError:
        print('Connection from {} cancelled'.format(address))
    finally:
        writer.close()
        yield from writer.wait_closed()

if __name__ == '__main__':
    address = zen_utils.parse_command_line('asyncio server using coroutine')
    loop = asyncio.get_event_loop()
    coro = asyncio.start_server(handle_conversation, *address)
    server = loop.run_until_complete(coro)
    print('Listening at {}'.format(address))
    try:
        loop.run_forever()
    except KeyboardInterrupt:
        print('Server shutting down...')
    finally:
        server.close()
        loop.run_until_complete(server.wait_closed())
        loop.close()
