========
User API
========
The methods in qpsphere for determining radius and refractive index
of spherical objects from quantitative phase images can be divided into
edge-based (:py:mod:`qpsphere.edgefit`) and image-based
(:py:mod:`qpsphere.imagefit`). The method :py:func:`qpsphere.analyze`
combines both in a user-convenient interface.

Basic usage
-----------
The high-level API of qpsphere heavily relies on :ref:`qpimage <qpimage:index>`
for accessing meta data to convert in-between units (e.g. pixel size  in
meters). If the experimental data file format is supported by 
:ref:`qpformat <qpformat:index>`, this leads to particularly clean and
simple code;

.. code-block:: python

   import qpformat
   import qpsphere
   
   # load an experimental data set
   ds = qpformat.load_data(path="path/to/data_file",
                           # set pixel size in meters
                           meta_data={"pixel size": .12e-6}
                           )
   # get QPImage instance (also contains meta data, e.g. pixel size)
   qpi_sensor = ds.get_qpimage()
   # obtain the region of interest containing a spherical object
   qpi_object = qpi_sensor[100:300, 50:250]
   # determine the refractive index and radius of the object
   n, r = qpsphere.analyze(qpi=qpi_object,
                           # estimate of the object's radius in meters
                           r0=10e-6,
                           # OPD edge-detection approach
                           method="edge"
                           # OPD projection model
                           model="projection"
                           )

where ``n`` is the average refractive index (RI) and ``r`` is the radius
of the object in meters estimated by the optical path difference (OPD)
edge-detection approach.

.. _choose_method_model:

Choosing method and model
-------------------------
Although the OPD edge-detection approach is fast, it is inaccurate because it
is resolution-dependent and because it approximates light scattering by an
integral over the RI along straight lines. Higher accuracy can be achieved
by fitting a 2D model to the experimental phase image. When setting
``method="image"`` in the example above, the following models are available:

- "mie": a full Mie model (very slow)
- "mie-avg": a polarization-averaged Mie model (faster than "mie")
- "projection": an OPD projection model
- "rytov": the Rytov approximation
- "rytov-sc": the systematically corrected Rytov approximation

A comparison of these models can be found in :cite:`Mueller2018`.
