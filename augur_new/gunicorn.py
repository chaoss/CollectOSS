import multiprocessing

workers = multiprocessing.cpu_count() * 2 + 1
bind = 'unix:Augur.sock'
umask = 0o007
reload = True

#logging
accesslog = 'access.log'
errorlog = 'error.log'