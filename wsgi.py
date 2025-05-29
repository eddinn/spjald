import sys
import logging

# Ensure the app directory is in the Python path before imports.
sys.path.insert(0, "/var/www/html/fegurdspa/html/spjald")

from app import create_app

application = create_app()

logging.basicConfig(
    filename='/var/log/spjald/spjald.log',
    level=logging.INFO,
    format='%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
)