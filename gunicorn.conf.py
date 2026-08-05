"""
HiddenYatra — Gunicorn Production Configuration
Usage: gunicorn -c gunicorn.conf.py wsgi:app
"""
import multiprocessing
import os

# ── Server Socket ──
bind = os.environ.get('GUNICORN_BIND', '0.0.0.0:5000')

# ── Workers ──
# Rule of thumb: (2 × CPU cores) + 1
workers = int(os.environ.get('GUNICORN_WORKERS', multiprocessing.cpu_count() * 2 + 1))
threads = int(os.environ.get('GUNICORN_THREADS', 2))
worker_class = 'gthread'

# ── Timeouts ──
timeout = 30
graceful_timeout = 30
keepalive = 5

# ── Request Limits ──
max_requests = 1000          # Restart worker after N requests (prevent memory leaks)
max_requests_jitter = 50     # Add randomness to prevent all workers restarting at once
limit_request_line = 8190
limit_request_fields = 100

# ── Logging ──
accesslog = os.environ.get('GUNICORN_ACCESS_LOG', '-')   # '-' = stdout
errorlog = os.environ.get('GUNICORN_ERROR_LOG', '-')     # '-' = stderr
loglevel = os.environ.get('GUNICORN_LOG_LEVEL', 'info')
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s" %(D)sμs'

# ── Process Naming ──
proc_name = 'hiddenyatra'

# ── Security ──
# Forwarded headers (trust Nginx proxy)
forwarded_allow_ips = os.environ.get('FORWARDED_ALLOW_IPS', '127.0.0.1')
proxy_allow_ips = os.environ.get('PROXY_ALLOW_IPS', '127.0.0.1')

# ── Preloading ──
preload_app = True

# ── Hooks ──
def on_starting(server):
    server.log.info('HiddenYatra starting with %d workers', server.app.cfg.workers)

def on_reload(server):
    server.log.info('HiddenYatra reloading...')

def worker_exit(server, worker):
    server.log.info('Worker %s exited (pid: %s)', worker.age, worker.pid)
