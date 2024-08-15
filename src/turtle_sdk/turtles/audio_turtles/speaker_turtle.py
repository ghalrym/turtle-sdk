from typing import Callable

import numpy
from bale_of_turtles import ActionTurtle, use_state
from mini_tortoise_audio import Audio, VbCableAudio, VbCableIn, VbCableOut
from pydub import AudioSegment

from turtle_sdk.turtles.turtle_tool_maker import make_fn_key


def _detect_silence(audio_chunk: bytes, threshold: float):
    # Convert the audio chunk to numpy array
    audio_data = numpy.frombuffer(audio_chunk, dtype=numpy.int16)
    # Compute the absolute values of the audio data
    abs_audio_data = numpy.abs(audio_data)
    # Check if all the values are below the threshold
    return numpy.all(abs_audio_data < threshold)


class SpeakerTurtle(ActionTurtle):
    __slots__ = (
        "_stream",
        "_audio",
        "_interrupt_playback",
        "should_interrupt",
        "audio_bytes_key",
        "turtle_out",
    )

    def __init__(
        self,
        device: VbCableIn | VbCableOut | str,
        audio_bytes_key: str,
        should_interrupt: Callable[[], bool] | None = None,
    ):
        super().__init__()
        self._audio = (
            Audio(device, is_input=False)
            if isinstance(device, str)
            else VbCableAudio(device)
        )
        self._stream = None
        self._interrupt_playback = False
        self.should_interrupt = should_interrupt
        self.audio_bytes_key = audio_bytes_key
        self.turtle_out = use_state(make_fn_key("audio-speaker"), [audio_bytes_key])(
            self._turtle_out
        )

    def register(self, state):
        super(ActionTurtle, self).register(state)
        self._stream = self._audio.open()

    def invoke(self):
        while self.should_interrupt:
            self._interrupt_playback = self.should_interrupt()

    def _turtle_out(self, **kwargs) -> None:
        if (audio_bytes_out := kwargs.get(self.audio_bytes_key, None)) is None:
            return

        audio_segment = AudioSegment.from_file(audio_bytes_out, format="wav")
        chunk_size = 1024
        for i in range(0, len(audio_segment), chunk_size):
            if self._interrupt_playback:
                break

            # noinspection PyProtectedMember
            chunk = audio_segment[i : i + chunk_size]._data
            self._stream.write(chunk)
