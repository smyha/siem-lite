Configuration
=============

Environment Variables
---------------------

SIEM Lite uses environment variables for configuration. Create a `.env` file in the project root:

Database Configuration
^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: bash

   # SQLite (default)
   DATABASE_URL=sqlite:///./siem_lite.db
   
   # PostgreSQL
   DATABASE_URL=postgresql://user:password@localhost:5432/siem_lite
   
   # MySQL
   DATABASE_URL=mysql://user:password@localhost:3306/siem_lite

API Server Configuration
^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: bash

   # Server settings
   API_HOST=127.0.0.1
   API_PORT=8000
   DEBUG=false
   
   # Security
   SECRET_KEY=your-very-secure-secret-key-here
   
   # CORS settings
   ALLOWED_HOSTS=localhost,127.0.0.1
   CORS_ORIGINS=http://localhost:3000

Logging Configuration
^^^^^^^^^^^^^^^^^^^^^

.. code-block:: bash

   # Log level
   LOG_LEVEL=INFO
   
   # Log file (optional)
   LOG_FILE_PATH=/var/log/siem-lite/app.log
   
   # Log format
   LOG_FORMAT=json

Detection Rules Configuration
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: bash

   # SSH brute-force detection
   SSH_THRESHOLD=5
   SSH_TIME_WINDOW=300
   
   # Web attack detection
   WEB_THRESHOLD=10
   WEB_TIME_WINDOW=60
   
   # IP reputation checking
   ENABLE_IP_REPUTATION=true

Monitoring Configuration
^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: bash

   # Prometheus metrics
   ENABLE_METRICS=true
   METRICS_PORT=9090
   
   # Health check intervals
   HEALTH_CHECK_INTERVAL=30

Configuration Classes
---------------------

The configuration is managed through Pydantic models:

.. code-block:: python

   from siem_lite.utils.config import get_settings
   
   settings = get_settings()
   
   # Access configuration
   print(f"Database URL: {settings.database.url}")
   print(f"API Port: {settings.api.port}")
   print(f"Debug Mode: {settings.debug}")

Database Settings
^^^^^^^^^^^^^^^^^

.. autoclass:: siem_lite.utils.config.DatabaseSettings
   :members:

API Settings
^^^^^^^^^^^^

.. autoclass:: siem_lite.utils.config.APISettings
   :members:

Security Settings
^^^^^^^^^^^^^^^^^

.. autoclass:: siem_lite.utils.config.SecuritySettings
   :members:

Production Configuration
------------------------

For production deployments, ensure:

1. **Security settings:**

   .. code-block:: bash

      DEBUG=false
      SECRET_KEY=<strong-random-key>
      ALLOWED_HOSTS=yourdomain.com
      
2. **Database optimization:**

   .. code-block:: bash

      DATABASE_URL=postgresql://user:pass@host:5432/db
      DATABASE_POOL_SIZE=20
      DATABASE_MAX_OVERFLOW=30
      
3. **Performance settings:**

   .. code-block:: bash

      WORKERS=4
      MAX_CONNECTIONS=1000
      KEEPALIVE_TIMEOUT=75

4. **Monitoring and logging:**

   .. code-block:: bash

      LOG_LEVEL=WARNING
      ENABLE_METRICS=true
      SENTRY_DSN=https://your-sentry-dsn

Docker Configuration
--------------------

When using Docker, environment variables can be set in:

1. **docker-compose.yml:**

   .. code-block:: yaml

      environment:
        - DATABASE_URL=postgresql://user:pass@db:5432/siem_lite
        - API_HOST=0.0.0.0
        - DEBUG=false

2. **Environment file:**

   .. code-block:: bash

      # Create .env file
      echo "DATABASE_URL=postgresql://user:pass@db:5432/siem_lite" > .env

Configuration Validation
-------------------------

Configuration is automatically validated on startup. Invalid configurations will cause the application to fail with descriptive error messages.

.. code-block:: python

   # Manual validation
   from siem_lite.utils.config import validate_config
   
   try:
       settings = validate_config()
       print("Configuration is valid")
   except ValidationError as e:
       print(f"Configuration error: {e}")
