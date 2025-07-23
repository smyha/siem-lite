Contributing
============

We welcome contributions to SIEM Lite! This guide will help you get started.

Getting Started
---------------

1. **Fork the repository** on GitHub
2. **Clone your fork** locally:

   .. code-block:: bash

      git clone https://github.com/your-username/siem-lite.git
      cd siem-lite

3. **Set up development environment:**

   .. code-block:: bash

      python -m venv venv
      source venv/bin/activate  # Linux/macOS
      # or
      venv\Scripts\activate     # Windows
      
      pip install -r requirements-dev.txt
      pre-commit install

4. **Create a feature branch:**

   .. code-block:: bash

      git checkout -b feature/your-feature-name

Development Guidelines
----------------------

Code Style
^^^^^^^^^^

* Follow **PEP 8** for Python code style
* Use **type hints** for all function parameters and return values
* Write **comprehensive docstrings** for all public functions and classes
* Maximum line length: **88 characters** (Black formatter default)

Code Quality Tools
^^^^^^^^^^^^^^^^^^

We use several tools to maintain code quality:

.. code-block:: bash

   # Format code
   black siem_lite/ tests/
   isort siem_lite/ tests/
   
   # Lint code
   flake8 siem_lite/
   mypy siem_lite/
   
   # Run tests
   pytest --cov=siem_lite

Architecture Principles
^^^^^^^^^^^^^^^^^^^^^^^

* Follow **Clean Architecture** patterns
* Maintain **separation of concerns**
* Use **dependency injection** for testability
* Keep **business logic** in the domain layer
* **External dependencies** go in infrastructure layer

Commit Message Format
^^^^^^^^^^^^^^^^^^^^^

Use conventional commit format:

.. code-block::

   type(scope): description
   
   [optional body]
   
   [optional footer]

Types:
* **feat**: New feature
* **fix**: Bug fix
* **docs**: Documentation changes
* **style**: Code style changes
* **refactor**: Code refactoring
* **test**: Adding or updating tests
* **chore**: Maintenance tasks

Examples:

.. code-block::

   feat(api): add alert acknowledgment endpoint
   fix(domain): resolve issue with alert severity validation
   docs(readme): update installation instructions
   test(api): add comprehensive tests for health endpoint

Testing Requirements
--------------------

All contributions must include appropriate tests:

Unit Tests
^^^^^^^^^^

* **Minimum 80% code coverage** for new code
* Test all **public functions and methods**
* Use **mocks and fixtures** appropriately
* Follow **AAA pattern** (Arrange, Act, Assert)

.. code-block:: python

   def test_create_alert_success():
       # Arrange
       alert_data = {
           "alert_type": "Test Alert",
           "source_ip": "192.168.1.1",
           "details": "Test details"
       }
       
       # Act
       result = create_alert(alert_data)
       
       # Assert
       assert result.alert_type == "Test Alert"
       assert result.source_ip == "192.168.1.1"

Integration Tests
^^^^^^^^^^^^^^^^^

* Test **API endpoints** end-to-end
* Test **database interactions**
* Test **external service integrations**

.. code-block:: python

   def test_api_create_alert():
       response = client.post("/api/alerts", json=alert_data)
       assert response.status_code == 201
       assert response.json()["alert_type"] == "Test Alert"

Documentation Requirements
---------------------------

All contributions should include documentation:

Code Documentation
^^^^^^^^^^^^^^^^^^

* **Docstrings** for all public functions and classes
* **Type annotations** for all parameters and return values
* **Examples** for complex functions

.. code-block:: python

   def process_log_entry(log_entry: str, rules: List[DetectionRule]) -> List[Alert]:
       """
       Process a log entry and generate alerts based on detection rules.
       
       Args:
           log_entry: Raw log entry string to process
           rules: List of detection rules to apply
           
       Returns:
           List of alerts generated from the log entry
           
       Raises:
           ValidationError: If log_entry format is invalid
           
       Example:
           >>> rules = [SSHBruteForceRule(), WebAttackRule()]
           >>> alerts = process_log_entry("Failed login from 1.2.3.4", rules)
           >>> len(alerts)
           1
       """

API Documentation
^^^^^^^^^^^^^^^^^

* Update **OpenAPI schemas** for new endpoints
* Add **examples** in endpoint documentation
* Document **error responses**

RST Documentation
^^^^^^^^^^^^^^^^^

* Update relevant **.rst files** for new modules
* Add **usage examples**
* Update **installation instructions** if needed

Pull Request Process
--------------------

1. **Ensure all tests pass:**

   .. code-block:: bash

      pytest --cov=siem_lite --cov-report=term-missing

2. **Check code quality:**

   .. code-block:: bash

      black --check siem_lite/ tests/
      isort --check siem_lite/ tests/
      flake8 siem_lite/
      mypy siem_lite/

3. **Update documentation:**

   .. code-block:: bash

      cd docs/
      make html

4. **Create pull request** with:
   
   * **Clear title** describing the change
   * **Detailed description** of what was changed and why
   * **Link to any related issues**
   * **Screenshots** for UI changes
   * **Breaking changes** clearly marked

5. **Respond to review feedback** promptly

Pull Request Template
^^^^^^^^^^^^^^^^^^^^^

.. code-block:: markdown

   ## Description
   Brief description of changes made.
   
   ## Type of Change
   - [ ] Bug fix (non-breaking change which fixes an issue)
   - [ ] New feature (non-breaking change which adds functionality)
   - [ ] Breaking change (fix or feature that would cause existing functionality to not work as expected)
   - [ ] Documentation update
   
   ## Testing
   - [ ] Unit tests pass
   - [ ] Integration tests pass
   - [ ] Code coverage maintained/improved
   
   ## Checklist
   - [ ] Code follows project style guidelines
   - [ ] Self-review completed
   - [ ] Code is commented where necessary
   - [ ] Documentation updated
   - [ ] No breaking changes (or clearly documented)

Issue Reporting
---------------

When reporting bugs or requesting features:

Bug Reports
^^^^^^^^^^^

Include:

* **Environment details** (OS, Python version, etc.)
* **Steps to reproduce** the issue
* **Expected behavior**
* **Actual behavior**
* **Error messages** or logs
* **Code samples** if applicable

Feature Requests
^^^^^^^^^^^^^^^^

Include:

* **Clear description** of the feature
* **Use case** and justification
* **Proposed implementation** (if you have ideas)
* **Alternatives considered**

Security Issues
^^^^^^^^^^^^^^^

**Do not** report security issues in public GitHub issues.

Instead, email security concerns to: security@your-domain.com

Recognition
-----------

Contributors will be recognized in:

* **CHANGELOG.md** for each release
* **README.md** acknowledgments section
* **Documentation** contributors page

Code of Conduct
---------------

This project follows the Contributor Covenant Code of Conduct. By participating, you are expected to uphold this code.

Key points:

* **Be respectful** and inclusive
* **Be collaborative** and constructive
* **Focus on the best** for the community
* **Show empathy** towards other community members

Getting Help
------------

If you need help contributing:

* **GitHub Discussions** for general questions
* **GitHub Issues** for specific problems
* **Documentation** for technical details
* **Code comments** for implementation details

Thank you for contributing to SIEM Lite! 🎉
