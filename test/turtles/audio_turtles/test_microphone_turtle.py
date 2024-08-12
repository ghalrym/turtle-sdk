from unittest.mock import MagicMock, patch

import numpy
from mini_tortoise_audio import VbCableIn

from turtle_sdk.turtles.audio_turtles.microphone_turtle import MicrophoneTurtleMaker


# noinspection PyUnresolvedReferences
@patch("turtle_sdk.turtles.audio_turtles.microphone_turtle.VbCableAudio")
def test_turtle_maker_vb_init(mock_audio: MagicMock) -> None:
    maker = MicrophoneTurtleMaker(VbCableIn.CABLE_A_INPUT, False)
    assert maker._device == VbCableIn.CABLE_A_INPUT

    microphone = maker.make_microphone()
    mock_audio.assert_called_once_with(VbCableIn.CABLE_A_INPUT)
    assert microphone._stream is None
    assert microphone._threshold == 500
    assert microphone._frames_per_buffer == 1024
    assert microphone._pitch_audio is False


# noinspection PyUnresolvedReferences
@patch("turtle_sdk.turtles.audio_turtles.microphone_turtle.Audio")
def test_turtle_maker_str_init(mock_audio: MagicMock) -> None:
    maker = MicrophoneTurtleMaker("Microphone", True)
    assert maker._device == "Microphone"

    microphone = maker.make_microphone()
    mock_audio.assert_called_once_with("Microphone", is_input=True)
    assert microphone._stream is None
    assert microphone._threshold == 500
    assert microphone._frames_per_buffer == 1024
    assert microphone._pitch_audio is True


# noinspection PyUnresolvedReferences
@patch("turtle_sdk.turtles.audio_turtles.microphone_turtle.VbCableAudio")
def test_microphone_register(mock_audio: MagicMock) -> None:
    mock_audio().open.return_value = "123-turtle!"

    maker = MicrophoneTurtleMaker(VbCableIn.CABLE_A_INPUT, False)
    microphone = maker.make_microphone()
    assert microphone._stream is None
    microphone.register(MagicMock())
    assert microphone._stream == "123-turtle!"


@patch("turtle_sdk.turtles.audio_turtles.microphone_turtle.VbCableAudio")
def test_microphone_wait_for_input(mock_audio):
    # Setup
    stream = MagicMock()
    mock_audio().open.return_value = stream

    maker = MicrophoneTurtleMaker(VbCableIn.CABLE_A_INPUT, False)
    microphone = maker.make_microphone()
    microphone.register(MagicMock())

    # Test
    stream.read.side_effect = [
        numpy.array([401], dtype=numpy.int16).tobytes(),
        numpy.array([402], dtype=numpy.int16).tobytes(),
        numpy.array([403], dtype=numpy.int16).tobytes(),
        numpy.array([501], dtype=numpy.int16).tobytes(),
        numpy.array([502], dtype=numpy.int16).tobytes(),
        numpy.array([503], dtype=numpy.int16).tobytes(),
        numpy.array([504], dtype=numpy.int16).tobytes(),
        numpy.array([404], dtype=numpy.int16).tobytes(),
        numpy.array([405], dtype=numpy.int16).tobytes(),
    ]
    frames = microphone.wait_for_input([])
    assert frames == [numpy.array([501], dtype=numpy.int16).tobytes()]


@patch("turtle_sdk.turtles.audio_turtles.microphone_turtle.VbCableAudio")
def test_microphone_record_until_silence(mock_audio):
    # Setup
    stream = MagicMock()
    mock_audio().open.return_value = stream

    maker = MicrophoneTurtleMaker(VbCableIn.CABLE_A_INPUT, False)
    microphone = maker.make_microphone()
    microphone.register(MagicMock())

    # Test
    stream.read.side_effect = [
        numpy.array([502], dtype=numpy.int16).tobytes(),
        numpy.array([503], dtype=numpy.int16).tobytes(),
        numpy.array([504], dtype=numpy.int16).tobytes(),
        numpy.array([404], dtype=numpy.int16).tobytes(),
        numpy.array([405], dtype=numpy.int16).tobytes(),
        numpy.array([406], dtype=numpy.int16).tobytes(),
        numpy.array([407], dtype=numpy.int16).tobytes(),
    ]
    frames = microphone.record_until_silence(
        [numpy.array([501], dtype=numpy.int16).tobytes()]
    )
    assert frames == [
        numpy.array([501], dtype=numpy.int16).tobytes(),
        numpy.array([502], dtype=numpy.int16).tobytes(),
        numpy.array([503], dtype=numpy.int16).tobytes(),
        numpy.array([504], dtype=numpy.int16).tobytes(),
    ]
