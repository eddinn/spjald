#!/usr/bin/python3
import os
import sys
import logging
from spjald import app as application


# logging.basicConfig(stream=sys.stderr)
logging.basicConfig(filename='/var/www/html/fegurdspa/html/spjald/spjald.log', level=logging.ERROR)
sys.path.insert(0, "/var/www/html/fegurdspa/html/spjald")
