# TODO write or generate get-set-del_property()
# TODO property of a parent class
# TODO attribute of the instance type or of a parent class

from contextlib import contextmanager
from typing import Union, Container, Literal, Callable, Tuple, Any
from unittest.mock import patch

GET = object()
SET = object()
DEL = object()
ALL = frozenset({GET, SET, DEL})

_BREAK_ON_OPTIONS = Union[
    Literal[GET, SET, DEL, ALL],
    Container[Literal[GET, SET, DEL]]
]


class MyPropertyMock(property):
    def __init__(
        self,
        owner: type,
        prop_name: str,
        hook_get: Callable[[Any, type], None] = lambda instance, owner: None,
        hook_set: Callable[[Any, Any], None] = lambda instance, value: None,
        hook_del: Callable[[Any], None] = lambda instance: None,
    ):
        assert isinstance(owner, type), "“owner” argument must be a type"
        self.hook_get = hook_get
        self.hook_set = hook_set
        self.hook_del = hook_del
        # TODO should I specify a default?
        self.orig_prop = getattr(owner, prop_name)
        super().__init__()

    def __get__(self, instance, owner=None):
        self.hook_get(instance, owner)
        return self.orig_prop.__get__(instance, owner)

    def __set__(self, instance, value):
        self.hook_set(instance, value)
        return self.orig_prop.__set__(instance, value)

    def __delete__(self, instance):
        self.hook_del(instance)
        return self.orig_prop.__del__(instance)


@contextmanager
def set_property(cls: type, prop_name: str, hook=breakpoint):
    mocked_property = MyPropertyMock(cls, prop_name, hook_set=hook)
    with patch.object(cls, prop_name, new=mocked_property):
        yield mocked_property


@contextmanager
def set_attribute(cls: type, prop_name: str, hook=breakpoint):
    # Mock cls.__setattr__ such that
    #  - if it's called with prop_name, then it calls the hook first, and then
    #  - regardless of prop_name, it calls the saved_setattr
    saved_setattr = cls.__setattr__

    def __setattr__(self, name, value):
        if name == prop_name:
            hook(self, value)
        self.__dict__[name] = value

    with patch.object(cls, '__setattr__', __setattr__):
        # TODO can we yield anything meaningful here?
        yield None