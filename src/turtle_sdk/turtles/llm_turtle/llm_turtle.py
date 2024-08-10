from bale_of_turtles.tool_turtle import TurtleTool


class LlmTurtle(TurtleTool):

    def __init__(self, name: str):
        super().__init__()
        self.name = name
