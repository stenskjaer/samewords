from contextlib import contextmanager
from samewords.settings import settings

@contextmanager
def temp_settings(dictionary):
    global settings
    old = dict(settings)
    settings.update(dictionary)
    yield
    settings.update(old)
