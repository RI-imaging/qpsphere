========
User API
========
The methods in qpsphere for determining radius and refractive index
of spherical objects from quantitative phase images can be divided into
edge-based (:py:mod:`qpsphere.edgefit`) and image-based
(:py:mod:`qpsphere.imagefit`). The convenience method
:py:func:`qpsphere.analyze` combines both in a user-convenient
interface.

Basic usage
-----------
The high-level API of qpsphere heavily relies on :py:mod:`qpimage` for
accessing meta data to convert in-between units (e.g. pixel size  in
meters). If the experimental data file format is supported by 
:py:mod:`qpformat`, this leads to particularly clean and simple code;

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
                           # edge-based approach
                           method="edge"
                           )

where ``n`` is the average refractive index and ``r`` is the radius
of the object in meters.

Choosing method and model
-------------------------
Although the edge-based approach is fast, it is inaccurate because it
is resolution-dependent and because it is based on a phase projection
model. Higher accuracy can be achieved by fitting a 2D model to the
experimental phase image. Several models are available in qpsphere:

- "mie": an Mie model, polarization-averaged
- "projection": a simple optical path difference projection model
- "rytov": the Rytov approximation
- "rytov-sc": a systematically corrected Rytov approximation

We are currently preparing a manuscript with a detailed description
of these models.
