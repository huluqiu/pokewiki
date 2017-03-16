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


if __name__ == "__main__":
    s = Stack()
    s.push(1)
    print(s)
