"""Comparison of sphere models

TODO:
 - add Born and Rytov models
"""
import matplotlib.pylab as plt
import qpsphere


kwargs = {"radius": 10e-6,  # 10µm
          "sphere_index": 1.36,  # cell
          "medium_index": 1.335,  # PBS
          "wavelength": 647e-9,  # argon laser
          "grid_size": (20, 20)
          }

px_size = 3 * kwargs["radius"] / kwargs["grid_size"][0]
kwargs["pixel_size"] = px_size

# projection
qpi_proj = qpsphere.simulate(model="projection", **kwargs)

# mie
qpi_mie = qpsphere.simulate(model="mie", **kwargs)


kwargs = {"vmin": qpi_proj.pha.min(),
          "vmax": qpi_proj.pha.max()}

plt.subplot(121, title="projection")
plt.imshow(qpi_proj.pha, **kwargs)

plt.subplot(122, title="Mie (BHFIELD)")
plt.imshow(qpi_mie.pha, **kwargs)

plt.show()
