Installation
============

System Requirements
-------------------

* Python 3.11 or higher
* PostgreSQL (optional, SQLite used by default)
* Redis (optional, for caching)
* Docker and Docker Compose (for containerized deployment)

Basic Installation
------------------

1. **Clone the repository:**

   .. code-block:: bash

      git clone https://github.com/your-username/siem-lite.git
      cd siem-lite

2. **Create and activate a virtual environment:**

   .. code-block:: bash

      python -m venv venv
      
      # On Windows:
      venv\Scripts\activate
      
      # On Linux/macOS:
      source venv/bin/activate

3. **Install dependencies:**

   .. code-block:: bash

      # Production installation
      pip install -r requirements.txt
      
      # Development installation
      pip install -r requirements-dev.txt

4. **Initialize the database:**

   .. code-block:: bash

      python -c "from siem_lite.infrastructure.database import init_db; init_db()"

5. **Start the application:**

   .. code-block:: bash

      uvicorn siem_lite.main:app --reload --host 0.0.0.0 --port 8000

Docker Installation
-------------------

For a complete containerized deployment:

.. code-block:: bash

   # Start all services
   docker-compose up -d
   
   # Verify services are running
   docker-compose ps
   
   # View logs
   docker-compose logs -f siem-lite

Development Installation
------------------------

For development with all tools and testing frameworks:

.. code-block:: bash

   # Install development dependencies
   pip install -r requirements-dev.txt
   
   # Install pre-commit hooks
   pre-commit install
   
   # Run tests to verify installation
   pytest --cov=siem_lite

Environment Configuration
-------------------------

Create a `.env` file with your configuration:

.. code-block:: bash

   # Copy example configuration
   cp .env.example .env
   
   # Edit with your values
   # DATABASE_URL=sqlite:///./siem_lite.db
   # API_HOST=127.0.0.1
   # API_PORT=8000
   # DEBUG=false

Verification
------------

Verify your installation by accessing:

* **API**: http://localhost:8000
* **Interactive Documentation**: http://localhost:8000/docs
* **Health Check**: http://localhost:8000/api/health

.. code-block:: bash

   # Test API endpoint
   curl http://localhost:8000/api/health
   
   # Should return: {"status": "healthy"}
