class _TurtleToolMaker:
    TURTLE_KEY = 0


def make_fn_key(tag: str):
    _TurtleToolMaker.TURTLE_KEY += 1
    return f"{tag}-{_TurtleToolMaker.TURTLE_KEY}"
