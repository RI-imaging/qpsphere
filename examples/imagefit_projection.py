"""OPD projection image fit applied to an OPD simulation

This examples illustrates how the refractive index and radius of
a sphere can be determined using the 2D phase fitting algorithm.
"""
import matplotlib.pylab as plt

import qpsphere

# run simulation with projection model
r = 5e-6
n = 1.339
med = 1.333
c = (120, 110)
qpi = qpsphere.simulate(radius=r,
                        sphere_index=n,
                        medium_index=med,
                        wavelength=550e-9,
                        grid_size=(256, 256),
                        model="projection",
                        center=c)

# fit simulation with projection model
n_fit, r_fit, c_fit, qpi_fit = qpsphere.analyze(qpi=qpi,
                                                r0=4e-6,
                                                method="image",
                                                model="projection",
                                                imagekw={"verbose": 1},
                                                ret_center=True,
                                                ret_qpi=True)

# plot results
fig = plt.figure(figsize=(8, 3.5))
txtkwargs = {"verticalalignment": "bottom",
             "horizontalalignment": "right",
             "fontsize": 12}

ax1 = plt.subplot(121, title="ground truth (OPD projection)")
map1 = ax1.imshow(qpi.pha)
plt.colorbar(map1, ax=ax1, fraction=.046, pad=0.04, label="phase [rad]")
t1 = "n={:.3f}\nmed={:.3f}\nr={:.1f}µm\ncenter=({:d},{:d})".format(
    n, med, r * 1e6, c[0], c[1])
ax1.text(1, 0, t1, transform=ax1.transAxes, color="w", **txtkwargs)

ax2 = plt.subplot(122, title="OPD projection fit residuals")
map2 = ax2.imshow(qpi.pha - qpi_fit.pha, vmin=-.01, vmax=.01, cmap="seismic")
plt.colorbar(map2, ax=ax2, fraction=.046, pad=0.04, label="phase error [rad]")
t2 = "Δn/n={:.2e}\nΔr/r={:.2e}\nΔx={:.2e}\nΔy={:.2e}".format(
    abs(n - n_fit) / n, abs(r - r_fit) / r,
    c_fit[0] - c[0], c_fit[1] - c[1])
ax2.text(1, 0, t2, transform=ax2.transAxes, color="k", **txtkwargs)

plt.tight_layout()
plt.show()
