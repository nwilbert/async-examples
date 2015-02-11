"""
Simple Chat Server using asyncio, aiohttp and Server Sent Events.
"""

import asyncio
import logging
import sys
import json
import html
from http.client import NO_CONTENT, BAD_REQUEST

from aiohttp import web

import utils

log = logging.getLogger('chat')


class ChatApp(web.Application):
    """Chat application based on SSE."""

    def __init__(self, loop):
        super().__init__(loop=loop)
        self.router.add_route('GET', '/chat', self.get_static_client_page)
        self.router.add_route('POST', '/chat/messages/',
                              self.post_chat_message.__get__(self))
        self.router.add_route('GET', '/chat/messages/',
                              self.get_chat_messages.__get__(self))

        self._next_message = asyncio.Future()

    @staticmethod
    def get_static_client_page(_):
        """GET handler returning the static chat HTML page."""
        with open('client.html', 'rb') as fh:
            return web.Response(body=fh.read())

    @asyncio.coroutine
    def post_chat_message(self, request):
        """POST request handler for submitting new chat message."""
        json_data = yield from request.json()
        try:
            username = json_data['username']
            text = json_data['text']
        except KeyError:
            return web.Response(status=BAD_REQUEST)
        log.info(' {} as "{}" sent message "{}"'
                 .format(request.host, username, text))

        self._next_message.set_result({
            'author': html.escape(username),
            'text': html.escape(text)
        })
        self._next_message = asyncio.Future()

        # always set content-type due to Firefox Bug:
        # https://bugzilla.mozilla.org/show_bug.cgi?id=521301
        return web.Response(status=NO_CONTENT, content_type='text/html')

    @asyncio.coroutine
    def get_chat_messages(self, request):
        """GET SSE request handler, streaming the incoming chat messages."""
        # inspired by https://github.com/brutasse/asyncio-sse
        response = web.StreamResponse()
        response.headers.add('Content-Type', 'text/event-stream')
        response.headers.add('Cache-Control', 'no-cache')
        response.headers.add('Connection', 'keep-alive')
        response.start(request)
        response.write(b'retry: 1000\n')  # set retry interval to 1s

        while True:
            json_data = yield from asyncio.shield(self._next_message)
            self._send_event(json_data, response)

    @staticmethod
    def _send_event(json_data, response):
        str_data = json.dumps(json_data)
        for line in str_data.split('\n'):
            response.write('data: {}\n'.format(line).encode())
        response.write('id: fsd\n'.encode())
        response.write(b'\n')


def run_server(host, port):
    loop = asyncio.get_event_loop()

    @asyncio.coroutine
    def _start_app():
        app = ChatApp(loop)
        return (yield from loop.create_server(app.make_handler(),
                                              host=host, port=port))

    loop.run_until_complete(_start_app())
    try:
        loop.run_forever()
    except KeyboardInterrupt:
        pass
    finally:
        loop.close()


if __name__ == '__main__':
    port = 8080
    for potential_ip in utils.get_potential_ips():
        print('Chat is served at:\n{}:{}/chat'.format(potential_ip, port))
    logging.basicConfig(stream=sys.stdout, level=logging.INFO)
    run_server('0.0.0.0', port)

