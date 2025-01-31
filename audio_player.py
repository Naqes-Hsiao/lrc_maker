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
        self.__is_pause = True
        self.__sample = None
        self.__is_load = False

        self.__p = pyaudio.PyAudio()

    def get_file_length(self):
        return self.__audio.duration_seconds

    def load(self):
        self.__file_path = askopenfilename(filetypes=[("音频文件", "*.flac;*.mp3")])
        if self.__file_path:
            if self.__is_load:
                self.pause()
                self.__stream.close()
            self.__index = 0
            self.__audio = AudioSegment.from_file(self.__file_path)
            self.__audio = self.__audio.set_sample_width(2)
            self.__sample = np.array(self.__audio.get_array_of_samples()).reshape(-1, 2)
            self.__is_load = True
        return self.__file_path

    def _play(self):
        self.__stream = self.__p.open(
            format=self.__p.get_format_from_width(self.__audio.sample_width),
            channels=2, rate=self.__audio.frame_rate, output=True
        )
        while self.__is_play:
            self.__stream.write(self.__sample[self.__index:self.__index + 1].tobytes())
            self.__index += 1
            if self.__index == len(self.__sample) - 1:
                self.__is_play = False
                break

    def play(self):
        self.__is_play = True
        self.__is_pause = False
        self.__thread = Thread(target=self._play, daemon=True)
        self.__thread.start()

    def pause(self):
        self.__is_play = False
        self.__is_pause = True

    def get_position(self):
        return self.__index / len(self.__sample) * 100

    def set_position(self, position):
        self.__index = int(position / 100 * len(self.__sample))

    def restart(self):
        is_over = not self.__is_play and not self.__is_pause
        if is_over:
            self.pause()
            self.__index = 0
            self.__is_pause = True
        return is_over

    def reset(self):
        self.pause()
        self.__file_path = None
        self.__audio = None
        self.__thread = None
        self.__stream = None
        self.__index = 0
