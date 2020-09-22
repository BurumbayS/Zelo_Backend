import multiprocessing

name = 'zelo'
bind = '0.0.0.0:8001'
workers = multiprocessing.cpu_count() * 2 + 1

# For now it needs to be sync due to dramatiq problems
worker_class = 'sync'
# worker_class = 'gevent'
# reload = True
timeout = 30
preload = True
