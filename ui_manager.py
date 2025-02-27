import tkinter as tk
from tkinter import font
import tkinter.messagebox as msgbox
from audio_player import AudioPlayer
from lrc_manager import LrcManager


class UIManager:
    def __init__(self, window):
        self.window = window
        self.window.title("LrcMaker")
        self.window.geometry("1300x650")

        self.audio_player = AudioPlayer()
        self.lrc_manager = LrcManager()

        self.create_widgets()
        self._update_progress()

    def create_widgets(self):
        self._configure_layout()
        self._create_frames()
        self._create_progress_bar()
        self._create_buttons()
        self._create_lrc_text()

    def _configure_layout(self):
        self.window.rowconfigure(0, weight=1)
        self.window.rowconfigure(1, weight=1)
        self.window.columnconfigure(0, weight=2)
        self.window.columnconfigure(1, weight=1)

    def _create_frames(self):
        self.frame_left = tk.Frame(self.window)
        self.frame_left.grid(row=0, column=0, rowspan=2, pady=10)

        self.frame_right = tk.Frame(self.window)
        self.frame_right.grid(row=0, column=1, pady=10)

    def _create_progress_bar(self):
        self.progress = tk.Label(self.frame_right, text="00:00 / 00:00")
        self.progress.pack()
        self.progress_bar = tk.Scale(self.frame_right, orient=tk.HORIZONTAL, length=400)
        self.progress_bar.pack()
        self.progress_bar.bind("<ButtonPress-1>", lambda e: self.seek_progress(e, "start"))
        self.progress_bar.bind("<B1-Motion>", lambda e: self.seek_progress(e, "drag"))
        self.progress_bar.bind("<ButtonRelease-1>", lambda e: self.seek_progress(e, "end"))

    def _create_buttons(self):
        # 音频控制按钮
        frame_audio = tk.Frame(self.frame_right)
        frame_audio.pack()
        btns_audio = [
            ("-1s", lambda: self.change_progress(-1)),
            ("播放", self.toggle_play),
            ("+1s", lambda: self.change_progress(1))
        ]
        self._create_buttons_in_frame(frame_audio, btns_audio, 3)
        self.play_btn = frame_audio.winfo_children()[1]

        # 加载文件按钮
        frame_load = tk.Frame(self.frame_right)
        frame_load.pack()
        btns_load = [
            ("加载音频文件", self.load_audio),
            ("加载歌词文件", self.load_lrc)
        ]
        self._create_buttons_in_frame(frame_load, btns_load)
        self.load_audio_btn = frame_load.winfo_children()[0]
        self.load_lrc_btn = frame_load.winfo_children()[1]

        # 歌词管理按钮
        frame_lrc = tk.Frame(self.frame_right)
        frame_lrc.pack()
        btns_lrc = [
            ("撤销", lambda: self.modify_lrc("undo")),
            ("打轴", self.timestamp),
            ("重置歌词", lambda: self.modify_lrc("reset_lrc")),
            ("逐字调整", lambda: self.modify_lrc("change_timestamp")),
            ("重置", self.reset),
            ("保存", lambda: self.modify_lrc("save"))
        ]
        self._create_buttons_in_frame(frame_lrc, btns_lrc)

    def _create_buttons_in_frame(self, frame, btns, cols=2):
        for index, (text, command) in enumerate(btns):
            btn = tk.Button(frame, text=text, command=command)
            btn.grid(row=index // cols, column=index % cols, padx=10, pady=10)

    def _create_lrc_text(self):
        self.lrc_text = tk.Text(self.frame_left, width=100, height=50, font=("宋体", 12))
        self.lrc_text.pack()
        self.lrc_text.config(state=tk.DISABLED)
        self.lrc_text.tag_config("highlight", background="yellow", foreground="red")
        self.lrc_text.bind("<Button-1>", self.highlight_click)

    def adjust_time(self, time):
        minute, second = divmod(time, 60)
        if second < 10:
            second = f"0{int(second)}"
        else:
            second = f"{int(second)}"
        minute = f"0{int(minute)}"
        return minute, second

    def set_progress(self, time):
        length = self.audio_player.get_file_length()
        total_minute, total_second = self.adjust_time(length)
        current_minute, current_second = self.adjust_time(time)
        self.progress.config(
            text=f"{current_minute}:{current_second} / {total_minute}:{total_second}"
        )

    def _update_progress(self):
        if self.audio_player.is_play():
            self.progress_bar.set(self.audio_player.get_position())
            self.set_progress(self.progress_bar.get())
        elif self.audio_player.restart():
            self.progress_bar.set(0)
            self.play_btn.config(text="播放")
            self.set_progress(self.progress_bar.get())
        self.progress_bar.after(1000, self._update_progress)

    def seek_progress(self, _, action):
        if self.audio_player.is_load():
            if action == "start" and self.audio_player.is_play():
                self.audio_player.pause()
                self.play_btn.config(text="播放")
            elif action == "drag":
                self.audio_player.set_position(self.progress_bar.get())
            elif action == "end":
                self.audio_player.play()
                self.play_btn.config(text="暂停")
        elif not self.audio_player.is_load() and action == "end":
            msgbox.showerror("错误", "请先加载音频文件")
            self.progress_bar.set(0)

    def change_progress(self, seconds):
        self.seek_progress(None, "start")
        self.progress_bar.set(self.progress_bar.get() + seconds)
        self.seek_progress(None, "drag")
        self.seek_progress(None, "end")

    def load_audio(self):
        self.audio_player.pause()
        self.audio_player.load()
        if self.audio_player.is_load():
            self.load_audio_btn.config(text="重新加载音频文件")
            self.play_btn.config(text="播放")

            self.progress_bar.config(to=self.audio_player.get_file_length())

            self.progress_bar.set(self.audio_player.get_position())
            self.set_progress(self.progress_bar.get())

    def toggle_play(self):
        if self.audio_player.is_load():
            if not self.audio_player.is_play():
                self.audio_player.play()
                self.play_btn.config(text="暂停")
            else:
                self.audio_player.pause()
                self.play_btn.config(text="播放")
        else:
            msgbox.showerror("错误", "请先加载音频文件")

    def load_lrc(self):
        self.lrc_manager.load()
        if self.lrc_manager.is_load():
            self.load_lrc_btn.config(text="重新加载歌词文件")
            self._update_lrc()

    def timestamp(self):
        if self.lrc_manager.is_load():
            if self.audio_player.is_load():
                current_time = self.audio_player.get_position()
                self.lrc_manager.timestamp(current_time)
                self._update_lrc()
            else:
                msgbox.showerror("错误", "请先加载音频文件")
        else:
            msgbox.showerror("错误", "请先加载歌词文件")

    def modify_lrc(self, action):
        if self.lrc_manager.is_load():
            getattr(self.lrc_manager, action)()
            if action == "change_timestamp":
                msgbox.showinfo("提示", "修改成功")
            elif action == "save":
                msgbox.showinfo("提示", "保存成功")
            self._update_lrc()
        else:
            msgbox.showerror("错误", "请先加载歌词文件")

    def reset(self):
        self._reset_ui()
        self.audio_player.reset()
        self.lrc_manager.reset()
        msgbox.showinfo("提示", "重置成功")

    def _reset_ui(self):
        self.load_audio_btn.config(text="加载音频文件")
        self.load_lrc_btn.config(text="加载歌词文件")
        self.play_btn.config(text="播放")

        self.lrc_text.config(state=tk.NORMAL)
        self.lrc_text.delete("1.0", tk.END)
        self.lrc_text.config(state=tk.DISABLED)

        self.progress_bar.set(0)

    def highlight_click(self, _):
        line_num = int(self.lrc_text.index(tk.CURRENT).split(".")[0])
        if line_num % 2 != 0:
            self.lrc_text.tag_remove("highlight", "1.0", tk.END)
            self.lrc_manager.set_file_index((line_num - 1) >> 1)
            self._highlight(line_num)

    def _update_lrc(self):
        self.lrc_text.config(state=tk.NORMAL)
        self.lrc_text.delete("1.0", tk.END)
        for line in self.lrc_manager.get_file_lines():
            self.lrc_text.insert(tk.END, line + "\n")
        self.lrc_text.config(state=tk.DISABLED)
        line_num = (self.lrc_manager.get_file_index() << 1) + 1
        self._highlight(line_num)

    def _highlight(self, line_num):
        start_index = f"{line_num}.0"
        end_index = f"{line_num}.end"
        self.lrc_text.tag_add("highlight", start_index, end_index)
        self._scroll_lrc_text(line_num)

    def _scroll_lrc_text(self, line_num):
        # 如果行号为1，则不执行滚动操作
        if line_num == 1:
            return

        # 获取lrc_text中从1.0到end的行数
        line_count = self.lrc_text.count("1.0", "end", "displaylines")[0]
        # 获取lrc_text的字体
        text_font = font.Font(font=self.lrc_text["font"])
        # 获取每行的高度
        line_height = text_font.metrics("linespace")
        # 计算总高度
        total_height = line_count * line_height

        # 获取从1.0到当前行号的行数
        current_count = self.lrc_text.count("1.0", f"{line_num}.0", "displaylines")[0]
        # 计算当前行号的高度
        current_height = current_count * line_height

        # 获取lrc_text的半高度
        half_text_height = self.lrc_text.winfo_height() >> 1

        # 如果当前行号的高度大于半高度，则滚动到当前行号的位置
        if current_height > half_text_height:
            # 计算滚动百分比
            percent = (current_height - half_text_height) / total_height
            self.lrc_text.yview_moveto(percent)
        # 否则滚动到顶部
        else:
            self.lrc_text.yview_moveto(0)
