import numpy

from io import BytesIO

from bale_of_turtles import ActionTurtle, use_state
from mini_tortoise_audio import Audio, VbCableAudio, VbCableIn, VbCableOut
from pydub import AudioSegment
from typing import Callable

from turtle_sdk.turtles.turtle_tool_maker import TurtleToolMaker


def _detect_silence(audio_chunk: bytes, threshold: float):
    # Convert the audio chunk to numpy array
    audio_data = numpy.frombuffer(audio_chunk, dtype=numpy.int16)
    # Compute the absolute values of the audio data
    abs_audio_data = numpy.abs(audio_data)
    # Check if all the values are below the threshold
    return numpy.all(abs_audio_data < threshold)


class SpeakerTurtle(ActionTurtle):
    __slots__ = ("_stream", "_audio", "_interrupt_playback", "should_interrupt")

    def __init__(
        self,
        device: VbCableIn | VbCableOut | str,
        should_interrupt: Callable[[], bool] | None = None,
    ):
        super().__init__()
        if isinstance(device, str):
            self._audio = Audio(device, is_input=False)
        else:
            self._audio = VbCableAudio(device)
        self._stream = None
        self._interrupt_playback = False
        self.should_interrupt = should_interrupt

    def register(self, state):
        super(ActionTurtle, self).register(state)
        self._stream = self._audio.open()

    def invoke(self):
        while self.should_interrupt:
            self._interrupt_playback = self.should_interrupt()

    def turtle_out(self, *args, **kwargs):
        raise NotImplementedError()


class SpeakerTurtleMaker(TurtleToolMaker):
    __slots__ = ("_device", "_should_interrupt")

    def __init__(
        self,
        device: VbCableIn | str,
        should_interrupt: Callable[[], bool] | None = None,
    ):
        self._device = device
        self._should_interrupt = should_interrupt

    def make(self, audio_bytes_key: str, **kwargs) -> SpeakerTurtle:

        class _SpeakerTurtle(SpeakerTurtle):
            @use_state(self._make_fn_key("audio-speaker"), [audio_bytes_key])
            def turtle_out(self, **kwargs) -> None:
                if (audio_bytes_out := kwargs.get(audio_bytes_key, None)) is None:
                    return

                audio_segment = AudioSegment.from_file(audio_bytes_out, format="wav")
                chunk_size = 1024
                for i in range(0, len(audio_segment), chunk_size):
                    if self._interrupt_playback:
                        break

                    # noinspection PyProtectedMember
                    chunk = audio_segment[i : i + chunk_size]._data
                    self._stream.write(chunk)

        return _SpeakerTurtle(self._device, self._should_interrupt)
