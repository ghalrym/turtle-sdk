from io import BytesIO

import torchaudio
from bale_of_turtles import TurtleTool, use_state
from mini_tortoise_tts import TextToSpeech, safe_load_voice

from turtle_sdk.turtles.turtle_tool_maker import TurtleToolMaker


class MiniTortoiseTtsTurtle(TurtleTool):

    def __init__(self, voice: str):
        super().__init__()
        self.tts = TextToSpeech(safe_load_voice(voice))

    def say(self, mini_tortoise_tts_say: str, **kwargs):
        raise NotImplementedError()


class MiniTortoiseTtsTurtleMaker(TurtleToolMaker):

    def __init__(self, voice: str):
        self._voice = voice

    def make(
        self, text_to_say_key: str, response_key: str, **kwargs
    ) -> MiniTortoiseTtsTurtle:

        class _TtsTurtle(MiniTortoiseTtsTurtle):

            @use_state(self._make_fn_key("tortoise-tts"), [text_to_say_key])
            def say(self, **kwargs):
                text_to_say = kwargs.get(text_to_say_key, None)
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
                self.update_state(**{response_key: bytesio})

        return _TtsTurtle(self._voice)
