from contextlib import contextmanager
from unittest.mock import patch


class MyPropertyMock(property):
    def __init__(self, owner, prop_name):
        assert isinstance(owner, type), "“owner” argument must be a type"
        # TODO should I specify a default?
        self.__orig_prop = getattr(owner, prop_name)

    def __get__(self, instance, owner):
        return self.__orig_prop.__get__(instance, owner)

    def __set__(self, instance, value):
        breakpoint()
        return self.__orig_prop.__set__(instance, value)


@contextmanager
def set_property(cls, prop_name):
    mocked_property = MyPropertyMock(cls, prop_name)
    with patch.object(cls, prop_name, new=mocked_property):
        yield mocked_property