_data = []


def update(*args):
    _data[:] = args


def info():
    return tuple(_data)
