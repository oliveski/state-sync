import os
import logging
import numpy as np
import tkinter as tk
from tkinter import ttk, messagebox
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from scipy.optimize import brentq

from modules.factory import create_eos
from modules.loader import EoSLoader

equations_directory = "equations-of-state"


class MainApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.equations_path = os.path.join(os.path.dirname(__file__), equations_directory)
        self.loader = EoSLoader(self.equations_path)

        self.title("Main Window")
        self.file_selection()
        self.VT_selection()
        self.go_button()

    def file_selection(self):
        # Dropdown menu
        ttk.Label(self, text="Select file:").pack(pady=5)

        self.file_var1 = tk.StringVar()
        self.file_var2 = tk.StringVar()

        self.dropdown1 = ttk.Combobox(self, textvariable=self.file_var1)
        self.dropdown2 = ttk.Combobox(self, textvariable=self.file_var2)

        self.refresh_dropdown_files()

        self.dropdown1.bind('<<Opening>>', lambda e: self.refresh_files(e))
        self.dropdown1.pack(padx=20, pady=5)

        self.dropdown2.bind('<<Opening>>', lambda e: self.refresh_files(e))
        self.dropdown2.pack(padx=20, pady=5)

    def VT_selection(self):
        # Float inputs T and V
        frame = ttk.Frame(self)
        frame.pack(pady=10)

        ttk.Label(frame, text="T:").grid(row=0, column=0, padx=5)
        self.entry_T = ttk.Entry(frame)
        self.entry_T.grid(row=0, column=1, padx=5)

        ttk.Label(frame, text="V:").grid(row=1, column=0, padx=5)
        self.entry_V = ttk.Entry(frame)
        self.entry_V.grid(row=1, column=1, padx=5)

    def go_button(self):
        self.go_frame = ttk.Frame(self)
        self.go_frame.pack(pady=10)
        self.go_btn = ttk.Button(self.go_frame, text="Plot", command=self.spawn_graph).pack()

    def refresh_dropdown_files(self, event=None):
        try:
            self.equations_map = self.loader.available_equations()
            self.dropdown1["values"] = list(self.equations_map.keys())
            self.dropdown2["values"] = list(self.equations_map.keys())
        except FileNotFoundError:
            messagebox.showerror(f"Equations directory not found!")
    
    def load_equations(self):
        loader = EoSLoader(self.equations_path)

    def spawn_graph(self):
        try:
            self.T_val = float(self.entry_T.get())
            self.V_val = float(self.entry_V.get())
        except ValueError:
            tk.messagebox.showerror("Input Error", "Please enter valid float values for T and V")

        self.eq_file1 = self.equations_map[self.dropdown1.get()]
        self.eq_file2 = self.equations_map[self.dropdown2.get()]
        logging.info(f"Equation file 1 selected: {self.eq_file1}")
        logging.info(f"Equation file 2 selected: {self.eq_file2}")

        win = tk.Toplevel(self)
        win.title("Graph")
        fig = Figure(figsize=(6, 5), dpi=100)
        ax = fig.add_subplot(111)

        x = np.linspace(0.01, 100, 1000)
        f = lambda x: (x**2/10) - np.sqrt(x)*np.sin(x) + 1
        g = lambda x: 100*np.log(x) + 5*x
        y1 = f(x) # for graph
        y2 = g(x) # for graph

        ax.plot(x, y1, label='f')
        ax.plot(x, y2, label='g')
        ax.axhline(0, color='black', linewidth=0.5)
        ax.axvline(0, color='black', linewidth=0.5)
        ax.grid(True, alpha=0.3)
        ax.legend()
        ax.set_xlabel('P (GPa)')
        ax.set_ylabel('T (K)')
        self.canvas = FigureCanvasTkAgg(fig, master=win)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        ttk.Label(win, text=f"T={self.T_val}, V={self.V_val}").pack(pady=20)

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
    app = MainApp()
    app.mainloop()
