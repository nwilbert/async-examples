"""
Simple Chat Server using asyncio, aiohttp and Server Sent Events.
"""

import asyncio
import logging
import sys
import json
import html
from http.client import NO_CONTENT

from aiohttp import web

import utils

log = logging.getLogger()


class ChatApp(web.Application):

    def __init__(self, loop):
        super().__init__(loop=loop)
        self._next_message = asyncio.Future()
        self.router.add_route('GET', '/chat', self._get_client_page)
        self.router.add_route('POST', '/chat/messages/',
                              self._post_chat_message.__get__(self))
        self.router.add_route('GET', '/chat/messages/',
                              self._get_chat_messages.__get__(self))

    @staticmethod
    def _get_client_page(_):
        with open('client.html', 'rb') as fh:
            return web.Response(body=fh.read())


    @asyncio.coroutine
    def _post_chat_message(self, request):
        json_data = yield from request.json()
        self._next_message.set_result({
            'author': html.escape(json_data['username']),
            'text': html.escape(json_data['text'])
        })
        self._next_message = asyncio.Future()
        # content-type for https://bugzilla.mozilla.org/show_bug.cgi?id=521301
        return web.Response(status=NO_CONTENT, content_type='text/html')


    @asyncio.coroutine
    def _get_chat_messages(self, request):
        # see https://github.com/brutasse/asyncio-sse
        response = web.StreamResponse()
        response.headers.add('Content-Type', 'text/event-stream')
        response.headers.add('Cache-Control', 'no-cache')
        response.headers.add('Connection', 'keep-alive')
        response.start(request)
        response.write(b'retry: 1000\n')  # set retry interval to 1s
        while True:
            json_data = yield from asyncio.shield(self._next_message)
            self._send_sse(json_data, response)

    @staticmethod
    def _send_sse(json_data, response):
        str_data = json.dumps(json_data)
        for line in str_data.split('\n'):
            response.write('data: {}\n'.format(line).encode('utf-8'))
        response.write('id: fsd\n'.encode('utf-8'))
        response.write(b'\n')


def run_server():
    port = 8080
    for potential_ip in utils.get_potential_ips():
        print('Chat is served at:\n{}:{}/chat'.format(potential_ip, port))
    logging.basicConfig(stream=sys.stdout, level=logging.INFO)

    loop = asyncio.get_event_loop()
    app = ChatApp(loop)

    @asyncio.coroutine
    def _start_app(loop_, app_, host, port):
        return (yield from loop_.create_server(app_.make_handler(), host, port))

    loop.run_until_complete(_start_app(loop, app, '0.0.0.0', port))
    try:
        loop.run_forever()
    except KeyboardInterrupt:
        pass
    finally:
        loop.close()


if __name__ == '__main__':
    run_server()

