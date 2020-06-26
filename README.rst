qpsphere
========

|PyPI Version| |Tests Status Linux| |Tests Status Win| |Coverage Status| |Docs Status|


**qpsphere** is a Python3 library for analyzing spherical objects in quantitative phase imaging.


Documentation
-------------

The documentation, including the reference and examples, is available at
`qpsphere.readthedocs.io <https://qpsphere.readthedocs.io/en/stable/>`__.


Installation
------------

::

    pip install qpsphere


Testing
-------

::

    pip install -e .
    python setup.py test


Releases to PyPI
----------------
The wheel distribution of qpsphere includes binaries of the BHFIELD program
and are thus platform-specific. When creating the wheels, the ``plat-name``
command line argument must be set.

::

    # on Windows
    python setup.py sdist bdist_wheel --plat-name win_amd64
    # on Linux 
    python setup.py sdist bdist_wheel --plat-name manylinux1_x86_64


.. |PyPI Version| image:: https://img.shields.io/pypi/v/qpsphere.svg
   :target: https://pypi.python.org/pypi/qpsphere
.. |Tests Status Linux| image:: https://img.shields.io/travis/RI-imaging/qpsphere.svg?label=tests_linux
   :target: https://travis-ci.com/RI-imaging/qpsphere
.. |Tests Status Win| image:: https://img.shields.io/appveyor/ci/paulmueller/qpsphere/master.svg?label=tests_win
   :target: https://ci.appveyor.com/project/paulmueller/qpsphere
.. |Coverage Status| image:: https://img.shields.io/codecov/c/github/RI-imaging/qpsphere/master.svg
   :target: https://codecov.io/gh/RI-imaging/qpsphere
.. |Docs Status| image:: https://readthedocs.org/projects/qpsphere/badge/?version=latest
   :target: https://readthedocs.org/projects/qpsphere/builds/

