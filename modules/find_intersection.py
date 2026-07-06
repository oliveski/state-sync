import numpy as np
from scipy.optimize import brentq

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
