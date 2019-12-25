import os

from contextlib import contextmanager
from samewords.settings import settings

from samewords import __root__


__testroot__ = os.path.join(__root__, "test")


@contextmanager
def temp_settings(dictionary):
    global settings
    old = dict(settings)
    settings.update(dictionary)
    yield
    settings.update(old)
