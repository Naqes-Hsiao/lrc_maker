import tkinter as tk
import tkinter.messagebox as msgbox
from audio_player import AudioPlayer
from lrc_manager import LrcManager


class InterfaceManager:
    def __init__(self, window):
        self.window = window
        self.window.title("LrcMaker")
        self.window.geometry("1300x650")

        self.audio_player = AudioPlayer()
        self.lrc_manager = LrcManager()

        self.index = 0
        self.lines = 0
        self.length = 0

        self.create_widgets()
        self.update_progress()

    def create_widgets(self):
        self.window.rowconfigure(0, weight=1)
        self.window.rowconfigure(1, weight=1)

        self.window.columnconfigure(0, weight=2)
        self.window.columnconfigure(1, weight=1)

        # 创建一个Frame，用于放置左边组件
        frame_left = tk.Frame(self.window)
        frame_left.grid(row=0, column=0, rowspan=2, pady=10)

        # 创建一个Frame，用于放置右边组件
        frame_right = tk.Frame(self.window)
        frame_right.grid(row=0, column=1, pady=10)

        # 创建一个Frame，用于放置进度条
        frame_progress_bar = tk.Frame(frame_right)
        frame_progress_bar.pack()

        # 进度条
        self.progress_bar = tk.Scale(frame_progress_bar, from_=0, to=100, orient=tk.HORIZONTAL, length=400, tickinterval=10)
        self.progress_bar.pack(pady=10)
        self.progress_bar.bind("<ButtonPress-1>", self.start_drag)
        self.progress_bar.bind("<B1-Motion>", self.drag_progress)
        self.progress_bar.bind("<ButtonRelease-1>", self.change_progress)

        # 创建一个Frame，用于放置音频相关按钮
        frame_audio = tk.Frame(frame_right)
        frame_audio.pack()

        # 音频文件按钮
        self.audio_file_button = tk.Button(frame_audio, text="加载音频文件", command=self.load_audio_file)
        self.audio_file_button.grid(row=0, column=0, padx=10, pady=10)

        # 播放按钮
        self.play_button = tk.Button(frame_audio, text="播放", command=self.play_audio)
        self.play_button.grid(row=0, column=1, padx=10, pady=10)

        # 创建一个Frame，用于放置歌词相关按钮
        frame_lrc = tk.Frame(frame_right)
        frame_lrc.pack(side=tk.TOP)

        # 创建一个按钮，用于加载歌词文件
        self.lrc_file_button = tk.Button(frame_lrc, text="加载歌词文件", command=self.load_lrc_file)
        self.lrc_file_button.grid(row=0, column=0, padx=10, pady=10)

        # 创建一个按钮，用于撤销操作
        self.undo_button = tk.Button(frame_lrc, text="撤销", command=self.undo)
        self.undo_button.grid(row=0, column=1, padx=10, pady=10)

        # 创建一个按钮，用于打轴
        self.timestamp_button = tk.Button(frame_lrc, text="打轴", command=self.timestamp)
        self.timestamp_button.grid(row=0, column=2, padx=10, pady=10)

        # 创建一个按钮，用于逐字调整
        self.change_button = tk.Button(frame_right, text="逐字调整", command=self.change_timestamp)
        self.change_button.pack(pady=10)

        # 创建一个按钮，用于重置
        self.restart_button = tk.Button(frame_right, text="重置", command=self.reset)
        self.restart_button.pack(pady=10)

        # 创建一个Text，用于显示歌词
        self.lrc_text = tk.Text(frame_left, width=100, height=50, font=("宋体", 12))
        self.lrc_text.pack()
        self.lrc_text.config(state=tk.DISABLED)
        self.lrc_text.tag_config("highlight", background="yellow", foreground="red")
        self.lrc_text.bind("<Button-1>", self.highlight_line)

    def update_progress(self):
        if self.play_button.cget("text") == "暂停":
            _, position = self.audio_player.get_position()
            self.progress_bar.set(position)
            if self.audio_player.restart():
                self.progress_bar.set(0)
                self.play_button.config(text="播放")
        self.progress_bar.after(1000, self.update_progress)

    def start_drag(self, _):
        if self.audio_file_button.cget("text") == "重新加载音频文件":
            if self.play_button.cget("text") == "暂停":
                self.audio_player.pause()
                self.play_button.config(text="播放")

    def drag_progress(self, _):
        if self.audio_file_button.cget("text") == "重新加载音频文件":
            self.audio_player.set_position(self.progress_bar.get())

    def change_progress(self, _):
        if self.audio_file_button.cget("text") == "重新加载音频文件":
            self.audio_player.play()
            self.play_button.config(text="暂停")
        else:
            msgbox.showerror("错误", "请先加载音频文件")
            self.progress_bar.set(0)

    def load_audio_file(self):
        if self.audio_file_button.cget("text") == "加载音频文件":
            if self.audio_player.load():
                self.audio_file_button.config(text="重新加载音频文件")
        else:
            self.audio_player.reload()

    def play_audio(self):
        if self.audio_file_button.cget("text") == "重新加载音频文件":
            if self.play_button.cget("text") == "播放":
                self.audio_player.play()
                self.play_button.config(text="暂停")
            else:
                self.audio_player.pause()
                self.play_button.config(text="播放")
        else:
            msgbox.showerror("错误", "请先加载音频文件")

    def load_lrc_file(self):
        if self.lrc_file_button.cget("text") == "加载歌词文件":
            if self.lrc_manager.load():
                self.lrc_file_button.config(text="重新加载歌词文件")
                self.update_lrc()
                self.location(self.lines, 0, self.length - 1, 1)
                self.scroll_lrc_text()
        else:
            self.lrc_manager.reload()
            self.update_lrc()
            self.location(self.lines, 0, self.length - 1, 1)
            self.scroll_lrc_text()

    def undo(self):
        if self.lrc_file_button.cget("text") == "重新加载歌词文件":
            if self.audio_file_button.cget("text") == "重新加载音频文件":
                self.lrc_manager.undo(self.index)
                self.update_lrc()
                self.location(self.lines, self.index, 0, -1)
                self.scroll_lrc_text()
            else:
                msgbox.showerror("错误", "请先加载音频文件")
        else:
            msgbox.showerror("错误", "请先加载歌词文件")

    def timestamp(self):
        if self.lrc_file_button.cget("text") == "重新加载歌词文件":
            if self.audio_file_button.cget("text") == "重新加载音频文件":
                current_time, _ = self.audio_player.get_position()
                self.lrc_manager.timestamp(self.index, current_time)
                self.update_lrc()
                self.location(self.lines, self.index, self.length - 1, 1)
                if self.index > 5:
                    self.scroll_lrc_text()
            else:
                msgbox.showerror("错误", "请先加载音频文件")
        else:
            msgbox.showerror("错误", "请先加载歌词文件")

    def change_timestamp(self):
        if self.lrc_file_button.cget("text") == "重新加载歌词文件":
            if self.audio_file_button.cget("text") == "重新加载音频文件":
                self.lrc_manager.change_timestamp()
                msgbox.showinfo("提示", "修改成功")
                self.update_lrc()
                self.location(self.lines, 0, 0, 1)
                self.scroll_lrc_text()
            else:
                msgbox.showerror("错误", "请先加载音频文件")
        else:
            msgbox.showerror("错误", "请先加载歌词文件")

    def reset(self):
        self.audio_player.reset()
        self.lrc_manager.reset()
        self.index = 0
        self.lines = 0
        self.length = 0
        self.audio_file_button.config(text="加载音频文件")
        self.lrc_file_button.config(text="加载歌词文件")
        self.play_button.config(text="播放")
        self.progress_bar.set(0)

    def highlight_line(self, _):
        self.lrc_text.tag_remove("highlight", "1.0", tk.END)
        line_number = int(self.lrc_text.index(tk.CURRENT).split(".")[0])
        if ~(line_number ^ 1):
            start_index = f"{line_number}.0"
            end_index = f"{line_number}.end"
            self.lrc_text.tag_add("highlight", start_index, end_index)
            self.index = (line_number - 1) >> 1

    def update_lrc(self):
        self.lrc_text.config(state=tk.NORMAL)
        self.lrc_text.delete("1.0", tk.END)
        self.lines, self.length = self.lrc_manager.read()
        for line in self.lines:
            self.lrc_text.insert(tk.END, line + "\n")
        self.lrc_text.config(state=tk.DISABLED)

    def location(self, lines, start, end, direction):
        for line in lines[start:end:direction]:
            condition = (direction + 1 and "]" in line) or (direction - 1 and not "]" in line)
            if condition:
                self.index += direction
            else:
                break
        start_index = f"{(self.index << 1) + 1}.0"
        end_index = f"{(self.index << 1) + 1}.end"
        self.lrc_text.tag_add("highlight", start_index, end_index)

    def scroll_lrc_text(self):
        scroll_distance = (self.index - 5) * 3
        self.lrc_text.yview_scroll(scroll_distance, "units")
