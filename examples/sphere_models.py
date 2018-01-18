"""Comparison of sphere models

TODO:
 - add Born and Rytov models
"""
import matplotlib.pylab as plt
import qpsphere


kwargs = {"radius": 10e-6,  # 10µm
          "sphere_index": 1.334,  # cell
          "medium_index": 1.333,  # PBS
          "wavelength": 1000e-9,  # argon laser
          "grid_size": (20, 20),
          }

px_size = 3 * kwargs["radius"] / kwargs["grid_size"][0]
kwargs["pixel_size"] = px_size

# projection
qpi_proj = qpsphere.simulate(model="projection", **kwargs)

# mie
qpi_mie = qpsphere.simulate(model="mie avg", **kwargs)

# rytov
qpi_ryt = qpsphere.simulate(model="rytov", **kwargs)


kwargs = {"vmin": qpi_mie.pha.min(),
          "vmax": qpi_mie.pha.max()}

plt.subplot(221, title="projection")
plt.imshow(qpi_proj.pha, **kwargs)

plt.subplot(222, title="Mie average")
plt.imshow(qpi_mie.pha, **kwargs)

plt.subplot(223, title="Rytov")
plt.imshow(qpi_ryt.pha, **kwargs)

plt.show()
