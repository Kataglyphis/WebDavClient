WebDavClient documentation
==========================

.. rst-class:: hero-section

Download files and folders from a WebDAV host.

.. grid:: 2
   :gutter: 2

   .. grid-item-card:: Getting started
      :link: getting-started
      :link-type: doc

      Install a release wheel or the source; usage, tests and static analysis.

   .. grid-item-card:: API
      :link: webdavclient
      :link-type: doc

      ``WebDavClient`` lists a WebDAV folder over PROPFIND and downloads it, logging
      through Loguru. The binary wheels compile every module with Cython; the API is
      typed.


.. toctree::
   :maxdepth: 2
   :caption: Contents:

   README
   getting-started
   webdavclient
   CHANGELOG

Tests and coverage
==================

Published with the docs by the Linux x64 lane, from the image's pinned CPython; the
free-threaded report is its X.Yt twin.

* `Coverage report (HTML) <_static/coverage/index.html>`_ and `(XML) <_static/coverage.xml>`_
* `Test report <_static/test_results/pytest-report.html>`_
* `Free-threaded test report <_static/test_results/pytest-report-free-threaded.html>`_

Indices and tables
==================

* :ref:`genindex`
* :ref:`search`
