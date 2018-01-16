============
Introduction
============

.. toctree::
  :maxdepth: 2


The decoupling problem
======================
Quantitative phase imaging (QPI) measures the phase retardation :math:`\phi(x,y)`
introduced by an object, such as a cell, to a light field, usually a plane wave.
Under the assumption that light travels along straight lines, the measured phase
:math:`\phi(x,y)` can be described as the projection of the refractive index (RI)
:math:`n(x,y,z)` of the imaged object onto the detector plane

.. math::

	\phi(x,y) = \frac{2 \pi}{\lambda} \int (n(x,y,z) - n_\text{med}) \, dz,  

with the vacuum wavelength :math:`\lambda` of the imaging light and the
RI of the object-surrounding medium :math:`n_\text{med}`.
This equation describes a coupling between the RI of the imaged object and its shape:
From a single phase image, it is not possible to compute the RI of an object without
knowing its shape and vice versa. Moreover, it is not possible to infer the RI of an
object from its shape if the RI is not constant. Thus, in general, it is not possible
to solve the coupling problem in QPI.  
However, if the object has a spherical shape and if its
RI is constant, it is possible to infer the radius :math:`R` and the RI :math:`n`
from a single phase measurement. The equation above then reduces to

.. math::

	\phi(x,y) = \frac{4 \pi}{\lambda} (n - n_\text{med}) \cdot \sqrt{R^2 - (x-x_0)^2 - (y-y_0)^2}

with the lateral position of the sphere :math:`(x_0, y_0)`. Note that this approach is
often applied to suspended (spherical) cells. Even though cells are complex structured
objects, this approach yields good estimates for the average RI and radius.  


Why qpsphere?
=============
The purpose of qpsphere is to make our QPI image analysis tools
(:cite:`Schuermann2015` :cite:`Schuermann2016` :cite:`Mueller2018`)
available to other research groups.
QPsphere makes heavy use of `qpimage <https://qpimage.readthedocs.io/en/stable)>`_,
a resourceful QPI image manager and is a key component of our QPI analysis
software `DryMass <https://drymass.readthedocs.io/en/stable)>`_.
