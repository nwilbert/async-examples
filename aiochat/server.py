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

next_message = None


def get_static_page(_):
    with open('client.html', 'rb') as fh:
        return web.Response(body=fh.read())


@asyncio.coroutine
def post_message(request):
    global next_message
    json_data = yield from request.json()
    # TODO: bleach
    next_message.set_result({
        'author': json_data['username'],
        'text': json_data['text']
    })
    next_message = asyncio.Future()
    return web.Response(status=NO_CONTENT)


@asyncio.coroutine
def get_messages_sse(request):
    # see https://github.com/brutasse/asyncio-sse
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
        data = yield from asyncio.shield(next_message)
        send(data)


def _get_app(loop):
    global next_message
    next_message = asyncio.Future()
    app = web.Application(loop=loop)
    app.router.add_route('GET', '/chat', get_static_page)
    app.router.add_route('POST', '/chat/messages/', post_message)
    app.router.add_route('GET', '/chat/messages/sse', get_messages_sse)
    return app


def main():
    print('please open: localhost:8080/chat')
    logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)
    loop = asyncio.get_event_loop()
    app = _get_app(loop)
    loop.run_until_complete(_start_app(loop, app, '127.0.0.1', 8080))
    loop.run_forever()


@asyncio.coroutine
def _start_app(loop, app, host, port):
    return (yield from loop.create_server(app.make_handler(), host, port))


if __name__ == '__main__':
    main()

