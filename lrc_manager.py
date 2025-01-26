import tkinter.filedialog as tkfd


class LrcManager:
    def __init__(self):
        self.__file_path = None
        self.__file_length = 0
        self.__file_lines = []
        self.__file_index = 0

    def get_file_length(self):
        return self.__file_length

    def get_file_lines(self):
        return self.__file_lines

    def get_file_index(self):
        return self.__file_index

    def load(self):
        self.__file_path = tkfd.askopenfilename(filetypes=[("歌词文件", "*.lrc")])
        return self.__file_path

    def reload(self):
        temp_file_path = self.__file_path
        self.__file_path = tkfd.askopenfilename(filetypes=[("歌词文件", "*.lrc")])
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
        lines, _ = self.read()
        if "]" in lines[index]:
            lines[index] = lines[index].split("]")[1]
        self.write(lines)

    def timestamp(self, index, time):
        lines, _ = self.read()
        if "]" not in lines[index]:
            minute, second = divmod(time, 60)
            if second < 10:
                lines[index] = f"[0{int(minute)}:0{second:.3f}]{lines[index]}"
            else:
                lines[index] = f"[0{int(minute)}:{second:.3f}]{lines[index]}"
            self.write(lines)

    def change_timestamp(self):
        lines, length = self.read()
        for index in range(length):
            lrc = lines[index]
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
                    change_minute, change_second = self._adjust_time(change_minute, change_second)
                    character_lst[time_index] = f"{change_minute}:{change_second}{change_time[9:]}"
                lines[index] = "<".join(character_lst)
        self.write(lines)

    def _parse_time(self, time_str):
        minute, second = time_str.split(":")
        return int(minute[1:]), float(second[:6])

    def _calculate_time_difference(self, target_minute, target_second, change_minute, change_second):
        difference_minute = target_minute - change_minute
        difference_second = target_second - change_second
        return difference_minute, difference_second

    def _adjust_time(self, minute, second):
        if second < 0:
            second += 60
            minute -= 1
        elif second >= 60:
            second -= 60
            minute += 1
        if second < 10:
            second = f"0{second:.3f}"
        else:
            second = f"{second:.3f}"
        if minute < 10:
            minute = f"0{minute}"
        return minute, second

    def reset(self):
        self.__file_path = None
