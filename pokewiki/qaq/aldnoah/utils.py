import heapq


class Stack(object):
    def __init__(self):
        self._stack = []

    def push(self, e):
        self._stack.append(e)

    def pop(self, default=None):
        try:
            return self._stack.pop()
        except IndexError:
            return default

    def get(self, default=None):
        try:
            return self._stack[-1]
        except IndexError:
            return default

    def __len__(self):
        return len(self._stack)

    def __str__(self):
        return str(self._stack)

    __repr__ = __str__


class Heap(object):

    """Docstring for Heap. """

    def __init__(self, l=[], reverse=False, key=None):
        """TODO: to be defined1.

        """
        self._heap = []
        self._reverse = reverse
        self._key = key
        self._tag = 0
        for e in l:
            value = None
            if key:
                value = (key(e), self._tag, e)
                self._tag += 1
                if reverse:
                    value[0] = -value[0]
            else:
                value = e
            self._heap.append(value)
        heapq.heapify(self._heap)

    def push(self, value):
        if self._key:
            if self._reverse:
                heapq.heappush(self._heap, (-self._key(value), self._tag, value))
            else:
                heapq.heappush(self._heap, (self._key(value), self._tag, value))
            self._tag += 1
        else:
            if self._reverse:
                heapq.heappush(self._heap, -value)
            else:
                heapq.heappush(self._heap, value)

    def pop(self):
        try:
            value = heapq.heappop(self._heap)
            if self._key:
                value = value[2]
            return value
        except IndexError:
            return None


class LazyProperty(object):
    def __init__(self, func):
        self.func = func

    def __get__(self, instance, owner):
        if instance is None:
            return self
        else:
            value = self.func(instance)
            setattr(instance, self.func.__name__, value)
            return value
