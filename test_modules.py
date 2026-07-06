from modules.factory import create_eos
from modules.loader import EoSLoader

import matplotlib.pyplot as plt
import numpy as np

loader = EoSLoader()
print(loader.list_available())

parse_eq = loader.load("teste")

eq = create_eos(parse_eq)
# print(eq.decomposition(150.21, 300))


T = np.linspace(300, 500, 100)
P1 = eq(150.21, T)
# print(P1)

plt.plot(P1, T)
plt.ylabel("T")
plt.xlabel("P")
plt.show()
