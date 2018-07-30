# -*- coding: utf-8 -*-

"""ComPath is a project for using gene-centric (and later other types of entities) to compare pathway knowledge.

This package provides guidelines, tutorials, and tools for making standardized ``compath`` packages as well as a
unifying framework for integrating them.

Installation
------------
Easiest
~~~~~~~
Download the latest stable code from `PyPI <https://pypi.org/compath_utils>`_ with:

.. code-block:: sh

   $ python3 -m pip install compath_utils

Get the Latest
~~~~~~~~~~~~~~~
Download the most recent code from `GitHub <https://github.com/compath/compath_utils>`_ with:

.. code-block:: sh

   $ python3 -m pip install git+https://github.com/compath/compath_utils.git

For Developers
~~~~~~~~~~~~~~
Clone the repository from `GitHub <https://github.com/compath/compath_utils>`_ and install in editable mode with:

.. code-block:: sh

   $ git clone https://github.com/compath/compath_utils.git
   $ cd compath_utils
   $ python3 -m pip install -e .


Testing
-------
ComPath Utils is tested with Python3 on Linux using `Travis CI <https://travis-ci.org/compath/compath_utils>`_.
"""

from compath_utils.exc import *  # noqa: F401, F403
from compath_utils.manager import *  # noqa: F401, F403
from compath_utils.models import *  # noqa: F401, F403

__version__ = '0.1.0-dev'

__title__ = 'compath_utils'
__description__ = "A utilities package for ComPath"
__url__ = 'https://github.com/compath/compath_utils'

__author__ = 'Charles Tapley Hoyt and Daniel Domingo-Fernández'
__email__ = 'charles.hoyt@scai.fraunhofer.de'

__license__ = 'MIT License'
__copyright__ = 'Copyright (c) 2018 Charles Tapley Hoyt and Daniel Domingo-Fernández'
