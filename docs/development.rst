Development
===========

Setting Up Development Environment
-----------------------------------

1. **Clone and setup:**

   .. code-block:: bash

      git clone https://github.com/your-username/siem-lite.git
      cd siem-lite
      
      # Create virtual environment
      python -m venv venv
      source venv/bin/activate  # Linux/macOS
      # or
      venv\Scripts\activate     # Windows

2. **Install development dependencies:**

   .. code-block:: bash

      pip install -r requirements-dev.txt

3. **Install pre-commit hooks:**

   .. code-block:: bash

      pre-commit install

4. **Run tests to verify setup:**

   .. code-block:: bash

      pytest --cov=siem_lite

Code Structure
--------------

The project follows Clean Architecture principles:

.. code-block::

   siem_lite/
   ├── api/               # FastAPI endpoints
   ├── domain/            # Business logic
   ├── infrastructure/    # External integrations
   ├── utils/             # Shared utilities
   ├── cli.py             # Command-line interface
   └── main.py            # Application entry point

Development Workflow
--------------------

1. **Create a feature branch:**

   .. code-block:: bash

      git checkout -b feature/your-feature-name

2. **Make your changes with tests:**

   .. code-block:: bash

      # Add your code
      # Add corresponding tests in tests/
      
3. **Run quality checks:**

   .. code-block:: bash

      # Format code
      black siem_lite/
      isort siem_lite/
      
      # Lint code
      flake8 siem_lite/
      mypy siem_lite/
      
      # Run tests
      pytest --cov=siem_lite --cov-report=html

4. **Commit and push:**

   .. code-block:: bash

      git add .
      git commit -m "feat: add your feature description"
      git push origin feature/your-feature-name

Testing
-------

Running Tests
^^^^^^^^^^^^^

.. code-block:: bash

   # Run all tests
   pytest
   
   # Run with coverage
   pytest --cov=siem_lite --cov-report=html
   
   # Run specific test files
   pytest tests/test_api.py
   pytest tests/test_domain.py
   
   # Run with verbose output
   pytest -v

Test Structure
^^^^^^^^^^^^^^

.. code-block::

   tests/
   ├── conftest.py          # Test configuration and fixtures
   ├── test_api.py          # API endpoint tests
   ├── test_domain.py       # Domain logic tests
   ├── test_infrastructure.py  # Infrastructure tests
   └── fixtures/            # Test data

Writing Tests
^^^^^^^^^^^^^

.. code-block:: python

   import pytest
   from fastapi.testclient import TestClient
   from siem_lite.main import app
   
   client = TestClient(app)
   
   def test_health_endpoint():
       response = client.get("/api/health")
       assert response.status_code == 200
       assert response.json() == {"status": "healthy"}

Code Quality
------------

Code Formatting
^^^^^^^^^^^^^^^

.. code-block:: bash

   # Format Python code
   black siem_lite/ tests/
   
   # Sort imports
   isort siem_lite/ tests/

Linting
^^^^^^^

.. code-block:: bash

   # Check code style
   flake8 siem_lite/
   
   # Type checking
   mypy siem_lite/

Pre-commit Hooks
^^^^^^^^^^^^^^^^

The project uses pre-commit hooks to ensure code quality:

.. code-block:: yaml

   # .pre-commit-config.yaml
   repos:
     - repo: https://github.com/psf/black
       rev: 23.7.0
       hooks:
         - id: black
     - repo: https://github.com/pycqa/isort
       rev: 5.12.0
       hooks:
         - id: isort
     - repo: https://github.com/pycqa/flake8
       rev: 6.0.0
       hooks:
         - id: flake8

Documentation
-------------

Building Documentation
^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: bash

   # Build Sphinx documentation
   cd docs/
   make html
   
   # View documentation
   # Open docs/_build/html/index.html in browser

Adding Documentation
^^^^^^^^^^^^^^^^^^^^

1. **Add docstrings to all public functions:**

   .. code-block:: python

      def create_alert(alert_data: dict) -> Alert:
          """
          Create a new security alert.
          
          Args:
              alert_data: Dictionary containing alert information
              
          Returns:
              Alert: The created alert instance
              
          Raises:
              ValidationError: If alert_data is invalid
          """

2. **Update RST files for new modules:**

   .. code-block:: bash

      # Regenerate API documentation
      sphinx-apidoc -o docs/ siem_lite/ --force

Debugging
---------

Local Debugging
^^^^^^^^^^^^^^^

.. code-block:: bash

   # Run in debug mode
   DEBUG=true uvicorn siem_lite.main:app --reload --port 8000
   
   # With debugger
   python -m debugpy --listen 5678 --wait-for-client -m uvicorn siem_lite.main:app --reload

Docker Debugging
^^^^^^^^^^^^^^^^

.. code-block:: bash

   # Check container logs
   docker-compose logs -f siem-lite
   
   # Execute commands in container
   docker-compose exec siem-lite bash
   
   # Debug database
   docker-compose exec db psql -U postgres -d siem_lite

Performance Profiling
^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: bash

   # Profile with cProfile
   python -m cProfile -o profile.stats -m uvicorn siem_lite.main:app
   
   # Analyze with snakeviz
   pip install snakeviz
   snakeviz profile.stats

Database Migrations
-------------------

Using Alembic for database migrations:

.. code-block:: bash

   # Generate migration
   alembic revision --autogenerate -m "Add new table"
   
   # Apply migration
   alembic upgrade head
   
   # Rollback migration
   alembic downgrade -1

Adding New Features
-------------------

1. **Create domain entities first:**

   .. code-block:: python

      # siem_lite/domain/entities.py
      @dataclass
      class NewEntity:
          id: int
          name: str
          created_at: datetime

2. **Add repository interface:**

   .. code-block:: python

      # siem_lite/domain/interfaces.py
      class NewEntityRepository(ABC):
          @abstractmethod
          def create(self, entity: NewEntity) -> NewEntity:
              pass

3. **Implement repository:**

   .. code-block:: python

      # siem_lite/infrastructure/repositories.py
      class SqlNewEntityRepository(NewEntityRepository):
          def create(self, entity: NewEntity) -> NewEntity:
              # Implementation

4. **Add API endpoints:**

   .. code-block:: python

      # siem_lite/api/new_endpoints.py
      @router.post("/new-entities/")
      def create_new_entity(entity_data: dict):
          # Implementation

5. **Add comprehensive tests:**

   .. code-block:: python

      # tests/test_new_feature.py
      def test_create_new_entity():
          # Test implementation
