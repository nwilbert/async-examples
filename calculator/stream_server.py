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


async def client_handler(reader, writer):
    interpreter = expression_gen()
    response = next(interpreter)
    writer.write(PROMPT.format(response).encode())

    while True:
        message = (await reader.readline()).decode().strip()
        try:
            response = interpreter.send(message)
        except StopIteration as e:
            writer.write(RESULT.format(e.value).encode())
            writer.close()
            log.info('sent result {}'.format(e.value))
            return
        except InvalidValue:
            writer.write('invalid value\n'.encode())
            writer.close()
            log.warning('invalid input')
            return

        writer.write(PROMPT.format(response).encode())


def run_server(host, port):
    loop = asyncio.get_event_loop()
    server_coro = asyncio.start_server(client_handler, host=host, port=port,
                                       loop=loop)
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
