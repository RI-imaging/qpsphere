"""Refractive index determination for a single cell

This example illustrates how qpsphere can be used to determine
the radius and the refractive index of a spherical cell.
The hologram of the myeloid leukemia cell (HL60) on the left was
recorded using digital holographic microscopy (DHM).
In the quantitative phase image on the right, the detected cell
contour (white) and the subsequent circle fit (red) as well as the
resulting average radius and refractive index of the the cell
are shown. The setup used for recording this data is described in [1]_,
which also contains a description of the basic steps to determine
the position and radius of the cell and to subsequently compute
the average refractive index from the experimental phase data.
The experimental data is loaded and background-corrected using
:py:mod:`qpimage`.


.. [1] M. Schürmann, J. Scholze, P. Müller, C.J. Chan, A.E. Ekpenyong,
   K. Chalut, J. Guck, *Refractive index measurements of single,
   spherical cells using digital holographic microscopy* in Biophysical
   Methods in Cell Biology (ed. E.K. Paluch) 2015,
   `DOI:10.1016/bs.mcb.2014.10.016
   <https://dx.doi.org/10.1016/bs.mcb.2014.10.016>`_
"""
import matplotlib
import matplotlib.pylab as plt
import numpy as np
import qpimage
import qpsphere

# load the experimental data
edata = np.load("./data/hologram_cell.npy.npz")

# create QPImage instance
qpi = qpimage.QPImage(data=edata["data"],
                      bg_data=edata["bg_data"],
                      which_data="hologram",
                      meta_data={"wavelength": 633e-9,
                                 "pixel size": 0.107e-6,
                                 "medium index": 1.335
                                 }
                      )

# background correction
qpi.compute_bg(which_data=["amplitude", "phase"],
               fit_offset="fit",
               fit_profile="ramp",
               border_px=5,
               )

# determine radius and refractive index, guess the cell radius: 10µm
n, r, (cx, cy), edge = qpsphere.edgefit.analyze(qpi=qpi,
                                                r0=10e-6,
                                                ret_center=True,
                                                ret_edge=True)

# plot results
fig = plt.figure(figsize=(8, 4))
matplotlib.rcParams["image.interpolation"] = "bicubic"
holkw = {"cmap": "gray",
         "vmin": 0,
         "vmax": 200}
# hologram image
ax1 = plt.subplot(121, title="cell hologram")
map1 = ax1.imshow(edata["data"].T, **holkw)
plt.colorbar(map1, ax=ax1, fraction=.048, pad=0.04)
# phase image
ax2 = plt.subplot(122, title="phase image [rad]")
map2 = ax2.imshow(qpi.pha.T)
# edge
edgeplot = np.ma.masked_where(edge == 0, edge)
ax2.imshow(edgeplot.T, cmap="gray_r", interpolation="none")
# fitted circle center
plt.plot(cx, cy, "xr", alpha=.5)
# fitted circle perimeter
circle = plt.Circle((cx, cy), r/qpi["pixel size"],
                    color='r', fill=False, ls="dashed", lw=2, alpha=.5)
ax2.add_artist(circle)
# fitting results as text
info = "n={:.4F}\nr={:.2f}µm".format(n, r*1e6)
ax2.text(.8, .8, info, color="w", fontsize="13", verticalalignment="top")
plt.colorbar(map2, ax=ax2, fraction=.048, pad=0.04)
# disable axes
[ax.axis("off") for ax in [ax1, ax2]]

plt.tight_layout()
plt.show()
