from tkinter.filedialog import askopenfilename
import re


class LrcManager:
    def __init__(self):
        self.__file_path = None
        self.__file_lines = None
        self.__index = 0

    def get_file_length(self):
        return len(self.__file_lines)

    def get_file_lines(self):
        return self.__file_lines

    def get_index(self):
        return self.__index

    def set_index(self, index):
        self.__index = index

    def load(self):
        temp_file_path = self.__file_path
        self.__file_path = askopenfilename(filetypes=[("歌词文件", "*.lrc")])
        if self.__file_path:
            with open(self.__file_path, "r", encoding="utf-8") as file:
                self.__file_lines = file.readlines()
            self.__index = 0
            self._location(0, len(self.__file_lines) - 1, 1)
        else:
            self.__file_path = temp_file_path
        return self.__file_path

    def undo(self):
        if "]" in self.__file_lines[self.__index]:
            self.__file_lines[self.__index] = self.__file_lines[self.__index].split("]")[1]
        self._location(self.__index, 0, -1)

    def timestamp(self, time):
        if "]" not in self.__file_lines[self.__index]:
            minute, second = self._adjust_time(time)
            self.__file_lines[self.__index] = f"[{minute}:{second}]{self.__file_lines[self.__index]}"
        self._location(self.__index, len(self.__file_lines) - 1, 1)

    def _location(self, start, end, direction):
        for line in self.__file_lines[start:end:direction]:
            condition_timestamp = direction == 1 and "]" in line
            condition_undo = direction == -1 and not "]" in line
            if not (condition_timestamp or condition_undo):
                break
            self.__index += direction

    def change_timestamp(self):
        # 遍历歌词文件行数，并获取当前行
        for index, line in enumerate(self.__file_lines):
            # 判断歌词格式是否匹配，如果当前行包含"]"和"<"，则进行时间戳转换
            if "]" in line and "<" in line:
                # 将当前行按"<"分割，得到目标时间和转换时间
                str_lst = line.split("<")
                # 计算目标时间和转换时间的时间差
                difference_minute, difference_second = self._calculate_difference(str_lst)
                # 调整时间戳
                self._change_timstamp(str_lst, difference_minute, difference_second)
                # 将调整后的时间戳重新拼接
                self.__file_lines[index] = "<".join(str_lst)

    def _calculate_difference(self, str_lst):
        target_time, change_time = str_lst[0], str_lst[1]
        # 解析目标时间和转换时间，得到分钟和秒
        target_minute, target_second, _ = self._match_str(target_time)
        change_minute, change_second, _ = self._match_str(change_time)
        return target_minute - change_minute, target_second - change_second

    def _change_timstamp(self, str_lst, difference_minute, difference_second):
        for index, str in enumerate(str_lst[1:], 1):
            # 解析当前时间，得到分钟、 秒和歌词
            change_minute, change_second, lrc_str = self._match_str(str)
            # 将时间差加到当前时间上
            change_minute += difference_minute
            change_second += difference_second
            # 调整时间，确保分钟和秒在合理范围内
            change_minute, change_second = self._adjust_time(change_minute * 60 + change_second)
            # 将转换后的时间重新拼接
            str_lst[index] = f"{change_minute}:{change_second}{lrc_str}"

    def _match_str(self, str):
        pattern = re.compile(r"\[?0(\d):(\d{2}\.\d+)(.*\n?)")
        match = pattern.match(str)
        return int(match.group(1)), float(match.group(2)), match.group(3)

    def _adjust_time(self, time):
        minute, second = divmod(time, 60)
        if second < 10:
            second = f"0{second:.3f}"
        else:
            second = f"{second:.3f}"
        minute = f"0{int(minute)}"
        return minute, second

    def reset_lrc(self):
        for index in range(len(self.__file_lines)):
            if "]" not in self.__file_lines[index]:
                break
            self.__file_lines[index] = self.__file_lines[index].split("]")[1]
        self.__index = 0

    def save(self):
        with open(self.__file_path, "w", encoding="utf-8") as file:
            file.writelines(self.__file_lines)

    def reset(self):
        self.__file_path = None
        self.__index = 0
