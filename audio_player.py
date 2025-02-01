from tkinter.filedialog import askopenfilename
from pydub import AudioSegment
import pyaudio
from threading import Thread
import numpy as np


class AudioPlayer:
    def __init__(self):
        self.__thread = None
        self.__sample = None
        self.__stream = None
        self.__index = 0
        self.__is_play = False
        self.__is_pause = True
        self.__file_length = 0

        self.__p = pyaudio.PyAudio()

    def get_file_length(self):
        return self.__file_length

    def load(self):
        file_path = askopenfilename(filetypes=[("音频文件", "*.flac;*.mp3")])
        if file_path:
            if self.__is_play:
                self.pause()
                self.__stream.close()
            self.__index = 0
            audio = AudioSegment.from_file(file_path).set_sample_width(2)
            self.__file_length = audio.duration_seconds
            self.__sample = np.array(audio.get_array_of_samples()).reshape(-1, 2)
            self.__stream = self.__p.open(
                format=self.__p.get_format_from_width(audio.sample_width),
                channels=2, rate=audio.frame_rate, output=True
            )
        return file_path

    def _play(self):
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
