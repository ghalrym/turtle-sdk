from io import BytesIO

import torchaudio
from bale_of_turtles import TurtleTool, use_state
from mini_tortoise_tts import TextToSpeech, safe_load_voice


class MiniTortoiseTtsTurtle(TurtleTool):

    def __init__(self, voice: str):
        super().__init__()
        self.tts = TextToSpeech(safe_load_voice(voice))

    @use_state("mini-tortoise-tts-say", ["mini_tortoise_tts_say"])
    def say(self, mini_tortoise_tts_say: str, **kwargs):
        audio = self.tts.generate(mini_tortoise_tts_say)
        bytesio = BytesIO()
        torchaudio.save(
            bytesio, audio.squeeze(0).cpu(), 24000, format="wav", bits_per_sample=32
        )
        self.update_state(audio_out_byte=bytesio)
