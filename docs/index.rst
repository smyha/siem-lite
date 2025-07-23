.. SIEM Lite documentation master file, created by
   sphinx-quickstart on Wed Jul 23 14:10:01 2025.

🛡️ SIEM Lite Documentation
===========================

Welcome to **SIEM Lite**, a lightweight Security Information and Event Management system built with FastAPI, designed to detect, analyze and manage security events in real-time.

.. image:: https://img.shields.io/badge/python-v3.11+-blue.svg
   :target: https://python.org
   :alt: Python Version

.. image:: https://img.shields.io/badge/FastAPI-0.104+-green.svg
   :target: https://fastapi.tiangolo.com/
   :alt: FastAPI Version

.. image:: https://img.shields.io/badge/docker-ready-blue.svg
   :target: https://docker.com
   :alt: Docker Ready

.. image:: https://img.shields.io/badge/license-MIT-blue.svg
   :target: LICENSE
   :alt: License

Quick Start
-----------

Install dependencies:

.. code-block:: bash

   pip install -r requirements.txt

Start the server:

.. code-block:: bash

   uvicorn siem_lite.main:app --reload --host 0.0.0.0 --port 8000

Access the API documentation at: http://localhost:8000/docs

Key Features
------------

* 🔍 **Event Detection**: Real-time security log analysis
* 📊 **Web Dashboard**: Intuitive interface for monitoring and management
* 🚨 **Alert System**: Automatic notifications for critical events
* 📈 **Metrics & Reports**: Statistical analysis and report generation
* 🐳 **Containerization**: Easy deployment with Docker and Docker Compose
* 📊 **Monitoring**: Integration with Prometheus and Grafana

Table of Contents
=================

.. toctree::
   :maxdepth: 2
   :caption: API Reference:

   api/index
   domain/index
   infrastructure/index
   utils/index

.. toctree::
   :maxdepth: 2
   :caption: Modules:

   modules

.. toctree::
   :maxdepth: 1
   :caption: Additional Information:

   installation
   configuration
   development
   contributing

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

