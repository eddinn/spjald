#!/usr/bin/python3
import os
import sys
import logging
from app import create_app

application = create_app()

logging.basicConfig(filename='/var/log/spjald/spjald.log',
                    level=logging.INFO)
sys.path.insert(0, "/var/www/html/fegurdspa/html/spjald")
