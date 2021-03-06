#
#    Copyright (c) 2014+ Anton Tyurin <noxiouz@yandex.ru>
#    Copyright (c) 2014+ Evgeny Safronov <division494@gmail.com>
#    Copyright (c) 2011-2014 Other contributors as noted in the AUTHORS file.
#
#    This file is part of Cocaine.
#
#    Cocaine is free software; you can redistribute it and/or modify
#    it under the terms of the GNU Lesser General Public License as published
#    by the Free Software Foundation; either version 3 of the License, or
#    (at your option) any later version.
#
#    Cocaine is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
#    GNU Lesser General Public License for more details.
#
#    You should have received a copy of the GNU Lesser General Public License
#    along with this program. If not, see <http://www.gnu.org/licenses/>.
#

import datetime

from tornado import gen

from ..decorators import coroutine
from ..detail.asyncqueue import AsyncQueue
from ..exceptions import ChokeEvent


class RequestError(Exception):
    def __init__(self, code, reason):
        self.code = code
        self.reason = reason


class Stream(object):
    def __init__(self, io_loop):
        self._queue = AsyncQueue(io_loop=io_loop)
        self._done = False

    @coroutine
    def get(self, timeout=0):
        if timeout == 0:
            res = yield self._queue.get()
        else:
            deadline = datetime.timedelta(seconds=timeout)
            res = yield self._queue.get(deadline=deadline)

        if isinstance(res, Exception):
            raise res
        else:
            raise gen.Return(res)

    def push(self, item):
        self._queue.put_nowait(item)

    def done(self):
        return self._queue.put_nowait(ChokeEvent())

    def error(self, errnumber, reason):
        return self._queue.put_nowait(RequestError(errnumber, reason))


class RequestStream(Stream):
    def read(self, **kwargs):
        return self.get(**kwargs)

    def close(self):
        return self.done()
