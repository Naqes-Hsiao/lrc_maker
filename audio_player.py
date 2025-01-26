import tkinter.filedialog as tkfd
import pygame as pg


class AudioPlayer:
    def __init__(self):
        self.__file_path = None
        self.__is_play = False
        self.__file_length = 0
        self.__difference = 0
        self.__is_first_play = True

        pg.mixer.init()

    def get_file_length(self):
        return self.__file_length

    def load(self):
        self.__file_path = tkfd.askopenfilename(filetypes=[("音频文件", "*.mp3; *.flac")])
        if self.__file_path:
            pg.mixer.music.load(self.__file_path)
            self.__file_length = pg.mixer.Sound(self.__file_path).get_length()
        return self.__file_path

    def reload(self):
        temp_file_path = self.__file_path
        self.__file_path = tkfd.askopenfilename(filetypes=[("音频文件", "*.mp3; *.flac")])
        if not self.__file_path:
            self.__file_path = temp_file_path
        else:
            pg.mixer.music.stop()
            pg.mixer.music.unload()
            pg.mixer.music.load(self.__file_path)
            self.__file_length = pg.mixer.Sound(self.__file_path).get_length()

    def play(self):
        if self.__is_first_play:
            pg.mixer.music.play()
            self.__is_first_play = False
        else:
            pg.mixer.music.unpause()
        self.__is_play = True

    def pause(self):
        self.play()
        pg.mixer.music.pause()
        self.__is_play = False

    def restart(self):
        is_over = self.__is_play and not pg.mixer.music.get_busy()
        if is_over:
            pg.mixer.music.stop()
            self.__is_first_play = True
            self.__is_play = False
            self.__difference = 0
        return is_over

    def set_position(self, position):
        self.pause()
        target_time = position / 100 * self.__file_length
        pg.mixer.music.set_pos(target_time)
        self.__difference = target_time - pg.mixer.music.get_pos() / 1000

    def get_position(self):
        if self.__is_play:
            current_time = pg.mixer.music.get_pos() / 1000 + self.__difference
            position = current_time / self.__file_length * 100
            return position
        else:
            return 0

    def reset(self):
        pg.mixer.music.stop()
        pg.mixer.music.unload()
        self.__file_path = None
        self.__is_play = False
        self.__file_length = 0
        self.__difference = 0
        self.__is_first_play = True
