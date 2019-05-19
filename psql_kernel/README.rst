psql_kernel
===========

``psql_kernel`` is a simple example of a Jupyter kernel. This repository
complements the documentation on wrapper kernels here:

http://jupyter-client.readthedocs.io/en/latest/wrapperkernels.html

Installation
------------
To install ``psql_kernel`` from PyPI::

    python setup.py install
    python -m psql_kernel.install

Using the psql kernel
----------------------
**Notebook**: The *New* menu in the notebook should show an option for a psql docker container notebook.

**Console frontends**: To use it with the console frontends, add ``--kernel psql`` to
their command line arguments.
