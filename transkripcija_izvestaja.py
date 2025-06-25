from faster_whisper import WhisperModel
import tempfile

MODEL = WhisperModel('base')


def transcribe_file(data):
