from io import BytesIO

import numpy
from bale_of_turtles import ActionTurtle, use_state
from mini_tortoise_audio import Audio, VbCableAudio, VbCableIn, VbCableOut
from pydub import AudioSegment


def _detect_silence(audio_chunk, threshold):
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
        super().register(state)
        self._stream = self._audio.open()

    @use_state("turtle-audio-out", ["audio_out_byte"])
    def turtle_out(self, audio_out_byte: BytesIO | None = None, **kwargs) -> None:
        # Play the audio
        audio_segment = AudioSegment.from_file(audio_out_byte, format="wav")
        chunk_size = 1024
        for i in range(0, len(audio_segment), chunk_size):
            if self._interrupt_playback:
                break
            # noinspection PyProtectedMember
            chunk = audio_segment[i : i + chunk_size]._data
            self._stream.write(chunk)

    def invoke(self):
        while self.should_interrupt:
            self._interrupt_playback = self.should_interrupt()
