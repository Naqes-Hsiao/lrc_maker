import tkinter.filedialog as tkfd
from pydub import AudioSegment
import pyaudio
import threading
import numpy as np


class AudioPlayer:
    def __init__(self):
        self.__file_path = None
        self.__audio = None
        self.__thread = None

        self.__p = pyaudio.PyAudio()

    def load(self):
        self.__file_path = tkfd.askopenfilename(filetypes=[("音频文件", "*.flac;*.mp3")])
        if self.__file_path:
            self.__audio = AudioSegment.from_file(self.__file_path)
        return self.__file_path

    def reload(self):
        temp_file_path = self.__file_path
        self.__file_path = tkfd.askopenfilename(filetypes=[("音频文件", "*.flac;*.mp3")])
        if not self.__file_path:
            self.__file_path = temp_file_path
        else:
            self.__audio = AudioSegment.from_file(self.__file_path)

    def _play(self):
        self.__audio = self.__audio.set_sample_width(2)
        stream = self.__p.open(
            format=self.__p.get_format_from_width(self.__audio.sample_width),
            channels=self.__audio.channels,
            rate=self.__audio.frame_rate,
            output=True
        )
        sample = np.array(self.__audio.get_array_of_samples()).reshape(-1, 2)
        stream.write(sample)

    def play(self):
        self.__thread = threading.Thread(target=self._play)
        self.__thread.start()

    def pause(self):
        pass
