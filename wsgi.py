#!/usr/bin/python3

import os
import sys
import time
import traceback

# 0) Log immediately to confirm this file is used
with open('/tmp/spjald_wsgi_loaded.log', 'a') as f:
    f.write(f"{time.asctime()}: wsgi.py imported\n")

# 1) Ensure project root is on PYTHONPATH and cwd
PROJECT_ROOT = "/var/www/html/fegurdspa/html/spjald"
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)
os.chdir(PROJECT_ROOT)

# 2) Seed required env vars
os.environ.setdefault('FLASK_APP', 'spjald:create_app')
os.environ.setdefault('FLASK_ENV', 'production')
os.environ.setdefault('DEBUG', 'True')
os.environ.setdefault('SECRET_KEY', '5d2acbdcaa904c3689cafba77000a323')
os.environ.setdefault('SERVER_NAME', 'spjald.fegurdspa.is:80')
os.environ.setdefault(
    'DATABASE_URL',
    'mysql+pymysql://spjald:ed080781@192.168.86.101:3306/spjald'
)
os.environ.setdefault('ADMINS', 'root@eddinn.net')
os.environ.setdefault('POSTS_PER_PAGE', '25')
os.environ.setdefault('MAIL_SERVER', 'localhost')
os.environ.setdefault('MAIL_PORT', '25')

# 3) Attempt to create the app, logging any exceptions
try:
    from spjald import create_app
    application = create_app()
    with open('/tmp/spjald_wsgi_loaded.log', 'a') as f:
        f.write(f"{time.asctime()}: create_app() succeeded\n")
except Exception:
    err_path = '/tmp/spjald_wsgi_error.log'
    with open(err_path, 'a') as f:
        f.write(f"{time.asctime()}: Exception in wsgi.py\n")
        traceback.print_exc(file=f)
        f.write("\n")
    raise
