"""
Simple TCP server to expose the calculation interpreter.

Here we use the lower level Transport/Protocol API.

Clients can connect with telnet.
"""

import asyncio
import logging
import sys

from calculator.interpreter import expression_gen, InvalidValue
import utils

log = logging.getLogger()


class CalculatorProtocol(asyncio.Protocol):

    PROMPT = '{}\n> '
    RESULT = 'result: {}\n'

    def __init__(self):
        super().__init__()
        self._transport = None
        self._peername = None
        self._interpreter = expression_gen()

    def connection_made(self, transport):
        self._transport = transport
        self._peername = transport.get_extra_info('peername')
        log.info('connection from {}'.format(self._peername))
        response = next(self._interpreter)
        self._transport.write(self.PROMPT.format(response).encode())

    def data_received(self, data):
        try:
            message = data.decode().strip()
        except UnicodeDecodeError:
            log.warning('undecodable input from {}'.format(self._peername))
            return

        try:
            response = self._interpreter.send(message)
        except StopIteration as e:
            self._transport.write(self.RESULT.format(e.value).encode())
            self._transport.close()
            log.info('sent result {} to {}'.format(e.value, self._peername))
            return
        except InvalidValue:
            self._transport.write('invalid value\n'.encode())
            self._transport.close()
            log.warning('invalid input from {}'.format(self._peername))
            return
        self._transport.write(self.PROMPT.format(response).encode())

    def connection_lost(self, exc):
        log.info('connection closed to {}'.format(self._peername))


def run_server(host, port):
    loop = asyncio.get_event_loop()
    server_coro = loop.create_server(CalculatorProtocol, host=host, port=port)
    server = loop.run_until_complete(server_coro)
    try:
        loop.run_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.close()
        loop.run_until_complete(server.wait_closed())
        loop.close()


if __name__ == '__main__':
    port = 8080
    for potential_ip in utils.get_potential_ips():
        print('Use "telnet {} {}"\n'.format(potential_ip, port))
    logging.basicConfig(stream=sys.stdout, level=logging.INFO)
    run_server('0.0.0.0', port)
