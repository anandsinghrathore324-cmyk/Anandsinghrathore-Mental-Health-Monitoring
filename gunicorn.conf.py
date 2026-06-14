import os

# Dynamic port binding from environment variable, defaulting to 5000
port = os.environ.get("PORT", "5000")
bind = f"0.0.0.0:{port}"

# Gunicorn configuration parameters for deployment stability
workers = 2
threads = 4
timeout = 120
accesslog = "-"
errorlog = "-"
