"""
Simple Chat Server using asyncio, asyncio and Server Sent Events
"""

import asyncio
import logging
import sys
import json
from http.client import NO_CONTENT

from aiohttp import web


log = logging.getLogger()


def get_static_page(_):
    with open('client.html', 'rb') as fh:
        return web.Response(body=fh.read())


@asyncio.coroutine
def post_message(request):
    data = yield from request.json()
    # TODO: bleach
    return web.Response(status=NO_CONTENT)


@asyncio.coroutine
def get_messages_sse(request):
    # see http://aiohttp.readthedocs.org/en/latest/web.html?
    response = web.StreamResponse()
    response.headers.add('Content-Type', 'text/event-stream')
    response.headers.add('Cache-Control', 'no-cache')
    response.headers.add('Connection', 'keep-alive')
    response.start(request)

    def send(json_data):
        str_data = json.dumps(json_data)
        for line in str_data.split('\n'):
            response.write('data: {}\n'.format(line).encode('utf-8'))
        response.write(b'\n')

    while True:
        yield from asyncio.sleep(2)
        send({
            'author': 'Niko',
            'text': 'Hallo'
        })
        yield from asyncio.sleep(2)
        send({
            'author': 'Miri',
            'text': 'Bonjour'
        })


def _get_app(loop):
    app = web.Application(loop=loop)
    app.router.add_route('GET', '/chat', get_static_page)
    app.router.add_route('POST', '/chat/messages/', post_message)
    app.router.add_route('GET', '/chat/messages/sse', get_messages_sse)
    return app


def main():
    print('please open: localhost:8080/chat')
    logging.basicConfig(stream=sys.stdout, level=logging.INFO)
    loop = asyncio.get_event_loop()
    app = _get_app(loop)
    loop.run_until_complete(_start_app(loop, app, '127.0.0.1', 8080))
    loop.run_forever()


@asyncio.coroutine
def _start_app(loop, app, host, port):
    return (yield from loop.create_server(app.make_handler(), host, port))


if __name__ == '__main__':
    main()

