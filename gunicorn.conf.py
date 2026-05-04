# gunicorn.conf.py - Gunicorn Configuration for Cinematch
import multiprocessing
import os

# Server Socket
bind = "127.0.0.1:5000"
backlog = 2048

# Worker Processes
workers = multiprocessing.cpu_count() * 2 + 1
worker_class = "sync"
worker_connections = 1000
max_requests = 1000
max_requests_jitter = 50
timeout = 120
keepalive = 2

# Restart workers periodically
max_requests = 1000
max_requests_jitter = 100

# Logging
accesslog = "/var/www/cinema/logs/gunicorn_access.log"
errorlog = "/var/www/cinema/logs/gunicorn_error.log"
loglevel = "info"
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s"'

# Process naming
proc_name = "cinematch"

# Daemon settings
user = "grimdolf"
group = "grimdolf"
tmp_upload_dir = None

# SSL (handled by nginx)
forwarded_allow_ips = "127.0.0.1"
secure_scheme_headers = {
    'X-FORWARDED-PROTO': 'https',
}

# Preload app for better performance
preload_app = True

# Thread settings
threads = 2
thread_class = "sync"

# Security
limit_request_line = 4094
limit_request_fields = 100
limit_request_field_size = 8190

# Reload settings (disable in production)
reload = False