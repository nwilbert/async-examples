"""
Chat
"""

import asyncio
import logging
import sys
from aiohttp import web


log = logging.getLogger()


def static_page(request):
    with open('client.html', 'rb') as fh:
        return web.Response(body=fh.read())


def get_app(loop):
    app = web.Application(loop=loop)
    app.router.add_route('GET', '/chat', static_page)
    return app


def main():
    print('please open: localhost:8080/chat')
    log.addHandler(logging.StreamHandler(sys.stdout))
    log.setLevel(logging.INFO)

    loop = asyncio.get_event_loop()
    app = get_app(loop)

    @asyncio.coroutine
    def start_server():
        return (yield from loop.create_server(app.make_handler(),
                                              '127.0.0.1', 8080))
    loop.run_until_complete(start_server())
    loop.run_forever()


if __name__ == '__main__':
    main()

