import asyncio,zen_utils
#use callback
class ZenServer(asyncio.Protocol):

    def connection_made(self,transport):
        self.transport = transport
        self.address = transport.get_extra_info('peername')
        self.data = b''
        print('Connection from {}'.format(self.address))

    def data_received(self, data):
        self.data += data
        if self.data.endswith(b'?'):
            answer = zen_utils.get_answer(self.data)
            self.transport.write(answer)
            self.data = b''

    def connection_lost(self, exc):
        if exc:
            print('Client {} error: {}'.format(self.address,exc))
        elif self.data:
            print('Client {} sent but then closed'.format(self.address,self.data))
        else:
            print('Client {} closed connection'.format(self.address))