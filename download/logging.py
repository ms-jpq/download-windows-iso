from logging import INFO, StreamHandler, getLogger
from sys import stderr

log = getLogger(__name__)
log.setLevel(INFO)
log.addHandler(StreamHandler(stderr))
