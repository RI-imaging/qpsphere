"""Comparison of light-scattering models

The phase error map allows a comparison of the ability of
the modeling methods implemented in qpsphere to reproduce
the phase delay introduced by a dielectric sphere.
For a quantitative comparison, see reference :cite:`Mueller2018`.
"""
import matplotlib.pylab as plt
import qpsphere

kwargs = {"radius": 10e-6,  # 10µm
          "sphere_index": 1.380,  # cell
          "medium_index": 1.335,  # PBS
          "wavelength": 647.1e-9,  # krypton laser
          "grid_size": (200, 200),
          }

px_size = 3 * kwargs["radius"] / kwargs["grid_size"][0]
kwargs["pixel_size"] = px_size

# mie (long computation time)
qpi_mie = qpsphere.simulate(model="mie", **kwargs)

# mie averaged
qpi_mie_avg = qpsphere.simulate(model="mie-avg", **kwargs)

# rytov corrected
qpi_ryt_sc = qpsphere.simulate(model="rytov-sc", **kwargs)

# rytov
qpi_ryt = qpsphere.simulate(model="rytov", **kwargs)

# projection
qpi_proj = qpsphere.simulate(model="projection", **kwargs)

kwargs = {"vmin": -.5,
          "vmax": .5,
          "cmap": "seismic"}

plt.figure(figsize=(8, 6.8))

ax1 = plt.subplot(221, title="Mie (averaged)")
pmap = plt.imshow(qpi_mie.pha - qpi_mie_avg.pha, **kwargs)

ax2 = plt.subplot(222, title="Rytov (corrected)")
plt.imshow(qpi_mie.pha - qpi_ryt_sc.pha, **kwargs)

ax3 = plt.subplot(223, title="Rytov")
plt.imshow(qpi_mie.pha - qpi_ryt.pha, **kwargs)

ax4 = plt.subplot(224, title="projection")
plt.imshow(qpi_mie.pha - qpi_proj.pha, **kwargs)

# disable axes
for ax in [ax1, ax2, ax3, ax4]:
    ax.axis("off")
    plt.colorbar(pmap, ax=ax, fraction=.045, pad=0.04,
                 label="phase error [rad]")

plt.tight_layout(w_pad=0, h_pad=0)
plt.show()
