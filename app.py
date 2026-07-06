from modules.equation_of_state import EquationOfState
from modules.loader import EoSLoader
import tkinter as tk
from tkinter import ttk
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from scipy.optimize import brentq
import numpy as np


def find_intersection(f, g, x_min=0.1, x_max=100):
    """Find intersection of f(x) and g(x) within [x_min, x_max]"""
    F = lambda x: f(x) - g(x)
    
    # Scan for sign changes in the domain
    x_vals = np.linspace(x_min, x_max, 500)
    F_vals = F(x_vals)
    sign_changes = np.where(np.diff(np.sign(F_vals)))[0]
    
    roots = []
    for i in sign_changes:
        try:
            root = brentq(F, x_vals[i], x_vals[i+1])
            y = f(root)
            if 0 <= y <= 2000:  # Validate y constraint
                roots.append((root, y))
        except ValueError:
            continue
    return roots


class CurvePlotterApp:
    def __init__(self, root, functions):
        self.root = root
        self.root.title("Curve Intersection")

        # Test widget
        ttk.Label(self.root, text="test").pack()
        
        # Create figure with subplot
        fig = Figure(figsize=(6, 5), dpi=100)
        ax = fig.add_subplot(111)
        
        # Define x range
        x = np.linspace(0.01, 100, 1000)
        
        f = functions[0]
        g = functions[1]
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
        
        # Embed canvas in tkinter window
        self.canvas = FigureCanvasTkAgg(fig, master=root)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        
        # Find intersection point
        intersections = find_intersection(f, g)
        for intersect in intersections:
            intersection_x = intersect[0]
            intersection_y = intersect[1]
            ax.scatter([intersection_x], [intersection_y], color='red', s=50, 
                       marker='o', zorder=5, label=f'({intersection_x:.2f}, {intersection_y:.2f})')
        ax.legend()
    
    def update_curves(self, new_func1, new_func2):
        """Clear axis and replot with new functions (for iterative updates)"""
        pass  # Implementation depends on your needs

if __name__ == "__main__":
    f = lambda x: (x**2/10) - np.sqrt(x)*np.sin(x) + 1
    g = lambda x: 100*np.log(x) + 5*x
    functions = [f, g]
    root = tk.Tk()
    app = CurvePlotterApp(root, functions)
    root.mainloop()
