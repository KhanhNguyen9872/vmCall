# KhanhNguyen9872

try:
    __import__('colorama')
except (ImportError, ModuleNotFoundError):
    __import__('os').system("{} -m pip install colorama".format(__import__('sys').executable))

class stdout:
    def __init__(self) -> None:
        try:
            __import__('colorama').just_fix_windows_console()
        except:
            pass
        
        self.stdout = __import__('sys').stdout
        self.full_str = ""

    def hide_cursor(self) -> None:
        self.stdout.write('\033[?25l')

    def show_cursor(self) -> None:
        self.stdout.write('\033[?25h')

    def flush(self) -> None:
        self.stdout.flush()

    def print(self, string, end = "\n") -> None:
        return self.write(string + end)

    def write(self, string : str) -> None:
        self.stdout.write(string)
        self.flush()
        self.full_str += string

    def clear(self, add_line = 0) -> None:
        try:
            if self.full_str[-1] != "\n":
                self.stdout.write("\n")
        except IndexError:
            return None

        tmp = len(self.full_str[:-1].split("\n")) + add_line
        self.reset()

        for _ in range(tmp):
            self.stdout.write("\x1b[1A\x1b[2K")
        self.flush()

    def reset(self) -> None:
        self.full_str = ""

    def out(self) -> str:
        return self.full_str