import tkinter.filedialog as tkfd


class LrcManager:
    def __init__(self):
        self.file_path = None

    def load(self):
        self.file_path = tkfd.askopenfilename(filetypes=[("歌词文件", "*.lrc")])
        return self.file_path

    def reload(self):
        temp_file_path = self.file_path
        self.file_path = tkfd.askopenfilename(filetypes=[("歌词文件", "*.lrc")])
        if not self.file_path:
            self.file_path = temp_file_path

    def read(self):
        with open(self.file_path, "r", encoding="utf-8") as file:
            lines = file.readlines()
            return lines, len(lines)

    def write(self, lines):
        with open(self.file_path, "w", encoding="utf-8") as file:
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
                lines[index] = f"[0{minute}:0{second:.3f}]{lines[index]}"
            else:
                lines[index] = f"[0{minute}:{second:.3f}]{lines[index]}"
            self.write(lines)

    def change_timestamp(self):
        lines, length = self.read()
        for index in range(length):
            lrc = lines[index]
            if "]" in lines[index] and "<" in lines[index]:
                character_lst = lrc.split("<")

                target_time = character_lst[0].split(":")
                target_minute = int(target_time[0][1:])
                target_second = float(target_time[1][:-1])

                change_time = character_lst[1].split(":")
                change_minute = int(change_time[0])
                change_second = float(change_time[1][:6])

                difference_minute = target_minute - change_minute
                difference_second = target_second - change_second

                for time_index in range(1, len(character_lst)):
                    time = character_lst[time_index]
                    change_time_lst = time.split(":")
                    change_minute = int(change_time_lst[0])
                    change_second = float(change_time_lst[1][:6])

                    change_minute += difference_minute
                    change_second += difference_second

                    if change_second >= 60:
                        change_minute += 1
                        change_second -= 60
                    elif change_second < 0:
                        change_minute -= 1
                        change_second += 60

                    if change_minute < 10:
                        change_minute = f"0{change_minute}"
                    else:
                        change_minute = f"{change_minute}"

                    if change_second < 10:
                        change_second = f"0{change_second:.3f}"
                    else:
                        change_second = f"{change_second:.3f}"

                    character_lst[time_index] = f"{change_minute}:{change_second}{change_time_lst[1][6:]}"
                lines[index] = "<".join(character_lst)
        self.write(lines)

    def reset(self):
        self.file_path = None
