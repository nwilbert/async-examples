"""
Simple TCP server to expose the calculation interpreter.

Here we use the higher level Stream API.

Clients can connect with telnet.
"""

import asyncio
import logging
import sys

from calculator.interpreter import expression_gen, InvalidValue
import utils

log = logging.getLogger()

PROMPT = '{}\n> '
RESULT = 'result: {}\n'


@asyncio.coroutine
def handle_client(reader, writer):
    interpreter = expression_gen()
    writer.write(PROMPT.format(next(interpreter)).encode())
    while True:
        message = (yield from reader.readline()).decode().strip()
        try:
            reply = interpreter.send(message)

        except StopIteration as e:
            writer.write(RESULT.format(e.value).encode())
            yield from writer.drain()
            writer.close()
            log.info('sent result {}'.format(e.value))
            return

        except InvalidValue:
            writer.write('invalid value\n'.encode())
            yield from writer.drain()
            writer.close()
            log.warning('invalid input')
            return

        writer.write(PROMPT.format(reply).encode())
        yield from writer.drain()


def run_server():
    port = 8080
    for potential_ip in utils.get_potential_ips():
        print('Use "telnet {} {}"\n'.format(potential_ip, port))
    logging.basicConfig(stream=sys.stdout, level=logging.INFO)

    loop = asyncio.get_event_loop()
    server_coroutine = asyncio.start_server(handle_client, '0.0.0.0', port,
                                            loop=loop)
    server = loop.run_until_complete(server_coroutine)
    try:
        loop.run_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.close()
        loop.run_until_complete(server.wait_closed())
        loop.close()


if __name__ == '__main__':
    run_server()
