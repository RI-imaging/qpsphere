Installing qpsphere
===================

Qpsphere is written in pure Python and supports Python version 3.5
and higher. Qpsphere depends on several other scientific Python packages,
including:

 - `numpy <https://docs.scipy.org/doc/numpy/>`_,
 - `scipy <https://docs.scipy.org/doc/scipy/reference/>`_,
 - `lmfit <https://lmfit.github.io/lmfit-py/>`_ (contour fitting),
 - `scikit-image <http://scikit-image.org/>`_ (segmentation).
 - `qpimage <https://qpimage.readthedocs.io/en/stable/>`_ (phase data manipulation),
    

To install qpsphere, use one of the following methods
(package dependencies will be installed automatically):
    
* from `PyPI <https://pypi.python.org/pypi/qpsphere>`_:
    ``pip install qpsphere``
* from `sources <https://github.com/RI-imaging/qpsphere>`_:
    ``pip install .`` or 
    ``python setup.py install``
