import wave
from io import BytesIO

from bale_of_turtles import ActionTurtle
from mini_tortoise_audio import Audio, VbCableAudio, VbCableIn
from pydub import AudioSegment

from turtle_sdk.turtles.audio_turtles.speaker_turtle import _detect_silence
from turtle_sdk.turtles.turtle_tool_maker import TurtleToolMaker


class MicrophoneTurtle(ActionTurtle):
    __slots__ = (
        "_stream",
        "_audio",
        "_threshold",
        "_pitch_audio",
        "_frames_per_buffer",
    )

    def __init__(self, device: VbCableIn | str, pitch_audio: int | bool = False):
        super().__init__()
        self._audio = (
            VbCableAudio(device)
            if device.startswith("CABLE")
            else Audio(device, is_input=True)
        )
        self._stream = None
        self._threshold = 500
        self._frames_per_buffer = 1024
        self._pitch_audio = pitch_audio

    def register(self, state):
        super(ActionTurtle, self).register(state)
        self._stream = self._audio.open()

    def wait_for_input(self, frames: list[bytes]) -> list[bytes]:
        # Pre-recording phase: wait until sound is detected
        while True:
            data = self._stream.read(self._frames_per_buffer)
            if not _detect_silence(data, self._threshold):
                frames.append(data)
                return frames

    def record_until_silence(self, frames: list[bytes], silence_seconds=2):
        silent_chunks = 0
        silence_chunks_threshold = int(
            silence_seconds * self._audio.rate / self._frames_per_buffer
        )

        while True:
            data = self._stream.read(self._frames_per_buffer)
            frames.append(data)

            if _detect_silence(data, self._threshold):
                silent_chunks += 1
            else:
                silent_chunks = 0

            if silent_chunks > silence_chunks_threshold:
                break
        return frames[:-2]  # Remove last 2 frames of silence

    def get_audio_data(self, frames: list[bytes]) -> BytesIO:
        # Save the recording to a BytesIO object
        audio_buffer = BytesIO()
        wf = wave.open(audio_buffer, "wb")
        wf.setnchannels(self._audio.audio_channels)
        wf.setsampwidth(self._stream.get_sample_size(self._audio.audio_format))
        wf.setframerate(self._audio.rate)
        wf.writeframes(b"".join(frames))
        wf.close()
        audio_buffer.seek(0)
        return audio_buffer

    def invoke(self) -> None:
        while True:
            frames = []
            frames = self.wait_for_input(frames)
            frames = self.record_until_silence(frames)
            audio = self.get_audio_data(frames)
            if self._pitch_audio:
                audio = self.change_pitch(audio, self._pitch_audio)
            self.update_state(audio_in_bytes=audio)

    @staticmethod
    def change_pitch(audio_bytes_io, octaves):
        # Load the audio from the BytesIO object
        audio_segment = AudioSegment.from_file(audio_bytes_io, format="wav")

        # Change the pitch by altering the playback speed
        new_sample_rate = int(audio_segment.frame_rate * (2.0**octaves))

        # Create a new audio segment with the new sample rate
        # noinspection PyProtectedMember
        pitch_shifted_audio = audio_segment._spawn(
            audio_segment.raw_data, overrides={"frame_rate": new_sample_rate}
        )

        # Ensure the audio remains in the same format
        pitch_shifted_audio = pitch_shifted_audio.set_frame_rate(
            audio_segment.frame_rate
        )

        # Save the pitch-shifted audio back to a BytesIO object
        output_audio_io = BytesIO()
        pitch_shifted_audio.export(output_audio_io, format="wav")
        output_audio_io.seek(0)

        return output_audio_io


class MicrophoneTurtleMaker(TurtleToolMaker):
    __slots__ = ("_device", "_pitch_audio")

    def __init__(self, device: VbCableIn | str, pitch_audio: int | bool = False):
        self._device = device
        self._pitch_audio = pitch_audio

    def make(self, **kwargs) -> MicrophoneTurtle:
        return MicrophoneTurtle(self._device, self._pitch_audio)
