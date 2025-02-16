from ui_manager import UIManager
import tkinter as tk


if __name__ == '__main__':
    window = tk.Tk()
    interface_manager = UIManager(window)
    window.mainloop()
