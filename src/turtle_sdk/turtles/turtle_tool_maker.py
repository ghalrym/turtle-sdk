from bale_of_turtles import TurtleTool


class TurtleToolMaker:
    _TURTLE_KEY = 0

    @staticmethod
    def _make_fn_key(tag: str):
        TurtleToolMaker._TURTLE_KEY += 1
        return f"turtle-tool-maker-{tag}-{TurtleToolMaker._TURTLE_KEY}"

    def make(self, **kwargs) -> TurtleTool:
        raise NotImplementedError()
