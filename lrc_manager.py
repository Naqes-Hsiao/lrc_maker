from tkinter.filedialog import askopenfilename
import re


class LrcManager:
    def __init__(self):
        self.__file_path = None
        self.__file_length = 0
        self.__file_lines = None
        self.__file_index = 0

    def get_file_length(self):
        return self.__file_length

    def get_file_lines(self):
        return self.__file_lines

    def get_file_index(self):
        return self.__file_index

    def set_file_index(self, index):
        self.__file_index = index

    def load(self):
        temp_file_path = self.__file_path
        self.__file_path = askopenfilename(filetypes=[("歌词文件", "*.lrc")])
        if self.__file_path:
            self._read()
        else:
            self.__file_path = temp_file_path
        return self.__file_path

    def _read(self):
        with open(self.__file_path, "r", encoding="utf-8") as file:
            self.__file_lines = file.readlines()
            self.__file_length = len(self.__file_lines)

    def _write(self, lines):
        with open(self.__file_path, "w", encoding="utf-8") as file:
            file.writelines(lines)

    def undo(self, index):
        if "]" in self.__file_lines[index]:
            self.__file_lines[index] = self.__file_lines[index].split("]")[1]
        self._write(self.__file_lines)

    def timestamp(self, index, time):
        if "]" not in self.__file_lines[index]:
            minute, second = self._adjust_time(time)
            self.__file_lines[index] = f"[{minute}:{second}]{self.__file_lines[index]}"
            self._write(self.__file_lines)

    def change_timestamp(self):
        # 遍历歌词文件行数，并获取当前行
        for index in range(self.__file_length):
            lrc_str = self.__file_lines[index]
            # 判断歌词格式是否匹配，如果当前行包含"]"和"<"，则进行时间戳转换
            if "]" in lrc_str and "<" in lrc_str:
                # 将当前行按"<"分割，得到目标时间和转换时间
                character_lst = lrc_str.split("<")
                # 计算目标时间和转换时间的时间差
                difference_minute, difference_second = self._calculate_difference(character_lst)
                # 调整时间戳
                self._change_timstamp(character_lst, difference_minute, difference_second)
                # 将调整后的时间戳重新拼接
                self.__file_lines[index] = "<".join(character_lst)
        self._write(self.__file_lines)

    def _change_timstamp(self, character_lst, difference_minute, difference_second):
        for time_index in range(1, len(character_lst)):
            change_time = character_lst[time_index]
            # 解析当前时间，得到分钟、 秒和歌词
            change_minute, change_second, lrc_str = self._match_str(change_time)
            # 将时间差加到当前时间上
            change_minute += difference_minute
            change_second += difference_second
            # 调整时间，确保分钟和秒在合理范围内
            change_minute, change_second = self._adjust_time(change_minute * 60 + change_second)
            # 将转换后的时间重新拼接
            character_lst[time_index] = f"{change_minute}:{change_second}{lrc_str}"

    def _calculate_difference(self, character_lst):
        target_time, change_time = character_lst[0], character_lst[1]
        # 解析目标时间和转换时间，得到分钟和秒
        target_minute, target_second, _ = self._match_str(target_time)
        change_minute, change_second, _ = self._match_str(change_time)
        return target_minute - change_minute, target_second - change_second

    def _match_str(self, time_str):
        pattern = re.compile(r"\[?0(\d):(\d{2}\.\d+)(.*\n?)")
        match = pattern.match(time_str)
        return int(match.group(1)), float(match.group(2)), match.group(3)

    def _adjust_time(self, time):
        minute, second = divmod(time, 60)
        if second < 10:
            second = f"0{second:.3f}"
        else:
            second = f"{second:.3f}"
        minute = f"0{int(minute)}"
        return minute, second

    def reset(self):
        self.__file_path = None
        self.__file_length = 0
        self.__file_lines = None
        self.__file_index = 0
