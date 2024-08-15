from io import BytesIO

import torchaudio
from bale_of_turtles import TurtleTool, use_state
from mini_tortoise_tts import TextToSpeech, safe_load_voice

from turtle_sdk.turtles.turtle_tool_maker import make_fn_key


class MiniTortoiseTtsTurtle(TurtleTool):
    __slots__ = ("tts", "say", "text_to_say_key", "response_key")

    def __init__(self, voice: str, text_to_say_key: str, response_key: str):
        super().__init__()
        self.tts = TextToSpeech(safe_load_voice(voice))
        self.text_to_say_key = text_to_say_key
        self.response_key = response_key
        self.say = use_state(make_fn_key("tortoise-tts"), [text_to_say_key])(self._say)

    def _say(self, **kwargs):
        text_to_say = kwargs.get(self.text_to_say_key, None)
        if not isinstance(text_to_say, str):
            return

        audio = self.tts.generate(text_to_say)
        bytesio = BytesIO()
        torchaudio.save(
            bytesio,
            audio.squeeze(0).cpu(),
            24000,
            format="wav",
            bits_per_sample=32,
        )
        self.update_state(**{self.response_key: bytesio})
