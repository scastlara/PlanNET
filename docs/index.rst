.. PlanNET documentation master file, created by
   sphinx-quickstart on Fri May 17 09:53:19 2019.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.



Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`



PlanNET documentation
===================================

.. toctree::
   :maxdepth: 4
   :caption: Models:

   modules/models/neo4j_models.rst
   modules/models/mysql_models.rst
   modules/models/downloaders.rst
   modules/models/colors.rst
   modules/models/plots.rst
   modules/models/gene_ontology.rst
   modules/models/neo4j_queries.rst


.. toctree::
   :glob:
   :maxdepth: 4
   :caption: Page views:

   modules/views/pages/*


----------

HTTP API
===================================


Views that define functions for returning JSON or HTML through programmatic HTTP 
requests. Used across the application in AJAX calls. Some can also be used by `curl`, 
`Perl` or any other program:

* :doc:`modules/views/http_api/plannet/get_card`
* :doc:`modules/views/http_api/plannet/downloader`
* :doc:`modules/views/http_api/plannet/get_fasta` 
* :doc:`modules/views/http_api/planexp/plots/plot_gene_expression`

Example:

.. code-block:: bash

    curl -H "Accept: application/json" \
         -H "Content-Type: application/json" \
         -X GET "https:/compgen.bio.ub.edu/PlanNET/get_fasta?genesymbol=SMESG000079934.1&database=Smesgene&type=sequence"

----------

.. toctree::
   :glob:
   :maxdepth: 4
   :caption: PlanNET:

   modules/views/http_api/plannet/*

.. toctree::
   :glob:
   :maxdepth: 4
   :caption: PlanExp General:

   modules/views/http_api/planexp/general/*


.. toctree::
   :glob:
   :maxdepth: 4
   :caption: PlanExp Plots:

   modules/views/http_api/planexp/plots/*
