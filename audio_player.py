from tkinter.filedialog import askopenfilename
from pydub import AudioSegment
import pyaudio
from threading import Thread
import numpy as np


class AudioPlayer:
    def __init__(self):
        self.__file_path = None
        self.__audio = None
        self.__thread = None
        self.__stream = None
        self.__is_play = False
        self.__index = 0
        self.__sample = None

        self.__p = pyaudio.PyAudio()

    def load(self):
        self.__file_path = askopenfilename(filetypes=[("音频文件", "*.flac;*.mp3")])
        if self.__file_path:
            self.__audio = AudioSegment.from_file(self.__file_path)
            self.__audio = self.__audio.set_sample_width(2)
            self.__sample = np.array(self.__audio.get_array_of_samples()).reshape(-1, 2)
        return self.__file_path

    def reload(self):
        self.__file_path = askopenfilename(filetypes=[("音频文件", "*.flac;*.mp3")])
        if self.__file_path:
            self.pause()
            self.__stream.close()
            self.__audio = AudioSegment.from_file(self.__file_path)
            self.__audio = self.__audio.set_sample_width(2)
            self.__sample = np.array(self.__audio.get_array_of_samples()).reshape(-1, 2)
            self.__index = 0

    def _play(self):
        self.__stream = self.__p.open(
            format=self.__p.get_format_from_width(self.__audio.sample_width),
            channels=2, rate=self.__audio.frame_rate, output=True
        )
        while self.__is_play:
            self.__stream.write(self.__sample[self.__index:self.__index + 1].tobytes())
            self.__index += 1

    def play(self):
        self.__is_play = True
        self.__thread = Thread(target=self._play, daemon=True)
        self.__thread.start()

    def pause(self):
        self.__is_play = False

    def get_position(self):
        return self.__index / len(self.__sample) * 100
