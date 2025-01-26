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

        self.create_widgets()
        self._update_progress()

    def create_widgets(self):
        self._configure_layout()
        self._create_frames()
        self._create_progress_bar()
        self._create_audio_buttons()
        self._create_lrc_buttons()
        self._create_additional_buttons()
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
        self.frame_progress_bar = tk.Frame(self.frame_right)
        self.frame_progress_bar.pack()

        self.progress_bar = tk.Scale(self.frame_progress_bar, from_=0, to=100, orient=tk.HORIZONTAL, length=400, tickinterval=10)
        self.progress_bar.pack(pady=10)
        self.progress_bar.bind("<ButtonPress-1>", self.start_drag)
        self.progress_bar.bind("<B1-Motion>", self.drag_progress)
        self.progress_bar.bind("<ButtonRelease-1>", self.end_drag)

    def _create_audio_buttons(self):
        self.frame_audio = tk.Frame(self.frame_right)
        self.frame_audio.pack()

        self.load_audio_button = tk.Button(self.frame_audio, text="加载音频文件", command=self.load_audio)
        self.load_audio_button.grid(row=0, column=0, padx=10, pady=10)

        self.play_button = tk.Button(self.frame_audio, text="播放", command=self.play)
        self.play_button.grid(row=0, column=1, padx=10, pady=10)

    def _create_lrc_buttons(self):
        self.frame_lrc = tk.Frame(self.frame_right)
        self.frame_lrc.pack(side=tk.TOP)

        self.load_lrc_button = tk.Button(self.frame_lrc, text="加载歌词文件", command=self.load_lrc)
        self.load_lrc_button.grid(row=0, column=0, padx=10, pady=10)

        self.undo_button = tk.Button(self.frame_lrc, text="撤销", command=self.undo)
        self.undo_button.grid(row=0, column=1, padx=10, pady=10)

        self.timestamp_button = tk.Button(self.frame_lrc, text="打轴", command=self.timestamp)
        self.timestamp_button.grid(row=0, column=2, padx=10, pady=10)

    def _create_additional_buttons(self):
        self.change_timestamp_button = tk.Button(self.frame_right, text="逐字调整", command=self.change_timestamp)
        self.change_timestamp_button.pack(pady=10)

        self.reset_button = tk.Button(self.frame_right, text="重置", command=self.reset)
        self.reset_button.pack(pady=10)

    def _create_lrc_text(self):
        self.lrc_text = tk.Text(self.frame_left, width=100, height=50, font=("宋体", 12))
        self.lrc_text.pack()
        self.lrc_text.config(state=tk.DISABLED)
        self.lrc_text.tag_config("highlight", background="yellow", foreground="red")
        self.lrc_text.bind("<Button-1>", self.highlight_line)

    def _update_progress(self):
        if self.play_button.cget("text") == "暂停":
            position = self.audio_player.get_position()
            self.progress_bar.set(position)
            if self.audio_player.restart():
                self.progress_bar.set(0)
                self.play_button.config(text="播放")
        self.progress_bar.after(1000, self._update_progress)

    def start_drag(self, _):
        if self.load_audio_button.cget("text") == "重新加载音频文件":
            if self.play_button.cget("text") == "暂停":
                self.audio_player.pause()
                self.play_button.config(text="播放")

    def drag_progress(self, _):
        if self.load_audio_button.cget("text") == "重新加载音频文件":
            self.audio_player.set_position(self.progress_bar.get())

    def end_drag(self, _):
        if self.load_audio_button.cget("text") == "重新加载音频文件":
            self.audio_player.play()
            self.play_button.config(text="暂停")
        else:
            msgbox.showerror("错误", "请先加载音频文件")
            self.progress_bar.set(0)

    def load_audio(self):
        if self.load_audio_button.cget("text") == "加载音频文件":
            if self.audio_player.load():
                self.load_audio_button.config(text="重新加载音频文件")
        else:
            self.audio_player.reload()

    def play(self):
        if self.load_audio_button.cget("text") == "重新加载音频文件":
            if self.play_button.cget("text") == "播放":
                self.audio_player.play()
                self.play_button.config(text="暂停")
            else:
                self.audio_player.pause()
                self.play_button.config(text="播放")
        else:
            msgbox.showerror("错误", "请先加载音频文件")

    def load_lrc(self):
        if self.load_lrc_button.cget("text") == "加载歌词文件":
            if self.lrc_manager.load():
                self.load_lrc_button.config(text="重新加载歌词文件")
                self._update_lrc()
                self._location(0, self.lrc_manager.get_file_length() - 1, 1)
                self._scroll_lrc_text()
        else:
            self.lrc_manager.reload()
            self._update_lrc()
            self._location(0, self.lrc_manager.get_file_length() - 1, 1)
            self._scroll_lrc_text()

    def undo(self):
        if self.load_lrc_button.cget("text") == "重新加载歌词文件":
            self.lrc_manager.undo(self.lrc_manager.get_file_index())
            self._update_lrc()
            self._location(self.lrc_manager.get_file_index(), 0, -1)
            self._scroll_lrc_text()
        else:
            msgbox.showerror("错误", "请先加载歌词文件")

    def timestamp(self):
        if self.load_lrc_button.cget("text") == "重新加载歌词文件":
            if self.load_audio_button.cget("text") == "重新加载音频文件":
                current_time = self.audio_player.get_position() / 100 * self.audio_player.get_file_length()
                self.lrc_manager.timestamp(self.lrc_manager.get_file_index(), current_time)
                self._update_lrc()
                self._location(self.lrc_manager.get_file_index(), self.lrc_manager.get_file_length() - 1, 1)
                if self.lrc_manager.get_file_index() > 5:
                    self._scroll_lrc_text()
            else:
                msgbox.showerror("错误", "请先加载音频文件")
        else:
            msgbox.showerror("错误", "请先加载歌词文件")

    def change_timestamp(self):
        if self.load_lrc_button.cget("text") == "重新加载歌词文件":
            self.lrc_manager.change_timestamp()
            msgbox.showinfo("提示", "修改成功")
            self._update_lrc()
            self._location(0, 0, 1)
            self._scroll_lrc_text()
        else:
            msgbox.showerror("错误", "请先加载歌词文件")

    def reset(self):
        self._reset_audio_player()
        self._reset_lrc_manager()
        self._reset_ui()
        self._reset_progress_bar()

    def _reset_audio_player(self):
        self.audio_player.reset()

    def _reset_lrc_manager(self):
        self.lrc_manager.reset()

    def _reset_ui(self):
        self.load_audio_button.config(text="加载音频文件")
        self.load_lrc_button.config(text="加载歌词文件")
        self.play_button.config(text="播放")

        self.lrc_text.config(state=tk.NORMAL)
        self.lrc_text.delete("1.0", tk.END)
        self.lrc_text.config(state=tk.DISABLED)

    def _reset_progress_bar(self):
        self.progress_bar.set(0)

    def highlight_line(self, _):
        self.lrc_text.tag_remove("highlight", "1.0", tk.END)
        line_number = int(self.lrc_text.index(tk.CURRENT).split(".")[0])
        if ~(line_number ^ 1):
            start_index = f"{line_number}.0"
            end_index = f"{line_number}.end"
            self.lrc_text.tag_add("highlight", start_index, end_index)
            self.lrc_manager.set_file_index((line_number - 1) >> 1)

    def _update_lrc(self):
        self.lrc_text.config(state=tk.NORMAL)
        self.lrc_text.delete("1.0", tk.END)
        self.lrc_manager.read()
        for line in self.lrc_manager.get_file_lines():
            self.lrc_text.insert(tk.END, line + "\n")
        self.lrc_text.config(state=tk.DISABLED)

    def _location(self, start, end, direction):
        for line in self.lrc_manager.get_file_lines()[start:end:direction]:
            condition_timestamp = direction == 1 and "]" in line
            condition_undo = direction == -1 and not "]" in line
            if condition_timestamp or condition_undo:
                self.lrc_manager.set_file_index(self.lrc_manager.get_file_index() + direction)
            else:
                break
        start_index = f"{(self.lrc_manager.get_file_index() << 1) + 1}.0"
        end_index = f"{(self.lrc_manager.get_file_index() << 1) + 1}.end"
        self.lrc_text.tag_add("highlight", start_index, end_index)

    def _scroll_lrc_text(self):
        scroll_distance = (self.lrc_manager.get_file_index() - 5) * 3
        self.lrc_text.yview_scroll(scroll_distance, "units")
