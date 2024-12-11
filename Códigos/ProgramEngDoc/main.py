#main.py

from tkinter import Tk
from app import App  # Certifique-se de que você está importando a classe correta

if __name__ == "__main__":
    root = Tk()
    app = App(root)
    root.mainloop()
