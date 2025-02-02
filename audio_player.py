from tkinter.filedialog import askopenfilename
from pydub import AudioSegment
import pyaudio
from threading import Thread
import numpy as np


class AudioPlayer:
    def __init__(self):
        self.__audio = None
        self.__sample = None
        self.__stream = None
        self.__index = 0
        self.__is_play = False
        self.__is_pause = True
        self.__has_thread = False

        self.__p = pyaudio.PyAudio()

    def get_file_length(self):
        return self.__audio.duration_seconds

    def load(self):
        file_path = askopenfilename(filetypes=[("音频文件", "*.flac;*.mp3")])
        if file_path:
            if self.__is_play:
                self.pause()
                self.__stream.close()
            self.__index = 0
            self.__audio = AudioSegment.from_file(file_path).set_sample_width(2)
            self.__sample = np.array(self.__audio.get_array_of_samples()).reshape(-1, 2)
            self.__stream = self.__p.open(
                format=self.__p.get_format_from_width(self.__audio.sample_width),
                channels=2, rate=self.__audio.frame_rate, output=True
            )
        return file_path

    def _play(self):
        while self.__is_play:
            self.__stream.write(self.__sample[self.__index:self.__index + 1].tobytes())
            self.__index += 1
            if self.__index == len(self.__sample) - 1:
                self.__is_play = False
                break
        self.__has_thread = False

    def play(self):
        self.__is_play = True
        self.__is_pause = False
        if not self.__has_thread:
            self.__has_thread = True
            thread = Thread(target=self._play, daemon=True)
            thread.start()

    def pause(self):
        self.__is_play = False
        self.__is_pause = True

    def get_position(self):
        return self.__index / self.__audio.frame_rate

    def set_position(self, position):
        self.__index = int(position * self.__audio.frame_rate)

    def restart(self):
        # 当播放结束时，并未按下暂停键，而是直接点击播放键时，需要重置播放状态
        is_over = not self.__is_play and not self.__is_pause
        if is_over:
            self.pause()
            self.__index = 0
            self.__is_pause = True
        return is_over

    def reset(self):
        self.pause()
        self.__index = 0
