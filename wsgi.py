# wsgi.py

#!/usr/bin/python3
import sys
import logging

# Ensure your project root is on PYTHONPATH
sys.path.insert(0, "/var/www/html/fegurdspa/html/spjald")

# Import the Flask app as 'application' for WSGI servers
from spjald import app as application

# Configure basic file‐based logging
logging.basicConfig(
    filename='/var/log/spjald/spjald.log',
    level=logging.INFO,
    format='%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
)