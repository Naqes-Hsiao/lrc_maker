from tkinter.filedialog import askopenfilename


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
        self.__file_path = askopenfilename(filetypes=[("歌词文件", "*.lrc")])
        return self.__file_path

    def reload(self):
        temp_file_path = self.__file_path
        self.__file_path = askopenfilename(filetypes=[("歌词文件", "*.lrc")])
        if not self.__file_path:
            self.__file_path = temp_file_path

    def read(self):
        with open(self.__file_path, "r", encoding="utf-8") as file:
            self.__file_lines = file.readlines()
            self.__file_length = len(self.__file_lines)

    def write(self, lines):
        with open(self.__file_path, "w", encoding="utf-8") as file:
            file.writelines(lines)

    def undo(self, index):
        if "]" in self.__file_lines[index]:
            self.__file_lines[index] = self.__file_lines[index].split("]")[1]
        self.write(self.__file_lines)

    def timestamp(self, index, time):
        if "]" not in self.__file_lines[index]:
            minute, second = self._adjust_time(time)
            self.__file_lines[index] = f"[{minute}:{second}]{self.__file_lines[index]}"
            self.write(self.__file_lines)

    def change_timestamp(self):
        for index in range(self.__file_length):
            lrc = self.__file_lines[index]
            if "]" in lrc and "<" in lrc:
                character_lst = lrc.split("<")
                target_time, change_time = character_lst[0], character_lst[1]
                target_minute, target_second = self._parse_time(target_time)
                change_minute, change_second = self._parse_time(change_time)
                difference_minute, difference_second = self._calculate_time_difference(target_minute, target_second, change_minute, change_second)
                for time_index in range(1, len(character_lst)):
                    change_time = character_lst[time_index]
                    change_minute, change_second = self._parse_time(change_time)
                    change_minute += difference_minute
                    change_second += difference_second
                    change_minute, change_second = self._adjust_time(change_minute * 60 + change_second)
                    character_lst[time_index] = f"{change_minute}:{change_second}{change_time[9:]}"
                self.__file_lines[index] = "<".join(character_lst)
        self.write(self.__file_lines)

    def _parse_time(self, time_str):
        minute, second = time_str.split(":")
        return int(minute[1:]), float(second[:6])

    def _calculate_time_difference(self, target_minute, target_second, change_minute, change_second):
        difference_minute = target_minute - change_minute
        difference_second = target_second - change_second
        return difference_minute, difference_second

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
