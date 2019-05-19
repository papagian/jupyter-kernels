bash_kernel
===========

``bash_kernel`` is a simple example of a Jupyter kernel. This repository
complements the documentation on wrapper kernels here:

http://jupyter-client.readthedocs.io/en/latest/wrapperkernels.html

Installation
------------
To install ``bash_kernel`` from PyPI::

    python setup.py install
    python -m bash_kernel.install

Using the bash kernel
---------------------
**Notebook**: The *New* menu in the notebook should show an option for a bash docker container notebook.

**Console frontends**: To use it with the console frontends, add ``--kernel bash`` to
their command line arguments.
