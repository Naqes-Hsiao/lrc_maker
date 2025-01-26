import tkinter.filedialog as tkfd
import pygame as pg


class AudioPlayer:
    def __init__(self):
        self.file_path = None
        self.is_play = False
        self.length = 0
        self.difference = 0
        self.is_first_play = True

        pg.mixer.init()

    def load(self):
        self.file_path = tkfd.askopenfilename(filetypes=[("音频文件", "*.mp3; *.flac")])
        if self.file_path:
            pg.mixer.music.load(self.file_path)
            self.length = pg.mixer.Sound(self.file_path).get_length()
        return self.file_path

    def reload(self):
        temp_file_path = self.file_path
        self.file_path = tkfd.askopenfilename(filetypes=[("音频文件", "*.mp3; *.flac")])
        if not self.file_path:
            self.file_path = temp_file_path
        else:
            pg.mixer.music.stop()
            pg.mixer.music.unload()
            pg.mixer.music.load(self.file_path)
            self.length = pg.mixer.Sound(self.file_path).get_length()

    def play(self):
        if self.is_first_play:
            pg.mixer.music.play()
            self.is_first_play = False
        else:
            pg.mixer.music.unpause()
        self.is_play = True

    def pause(self):
        self.play()
        pg.mixer.music.pause()
        self.is_play = False

    def restart(self):
        is_over = self.is_play and not pg.mixer.music.get_busy()
        if is_over:
            pg.mixer.music.stop()
            self.is_first_play = True
            self.is_play = False
            self.difference = 0
        return is_over

    def set_position(self, position):
        self.pause()
        target_time = position / 100 * self.length
        pg.mixer.music.set_pos(target_time)
        self.difference = target_time - pg.mixer.music.get_pos() / 1000

    def get_position(self):
        if self.is_play:
            current_time = pg.mixer.music.get_pos() / 1000 + self.difference
            position = current_time / self.length * 100
            return current_time, position
        else:
            return 0, 0

    def reset(self):
        pg.mixer.music.stop()
        pg.mixer.music.unload()
        self.file_path = None
        self.is_play = False
        self.length = 0
        self.difference = 0
        self.is_first_play = True
