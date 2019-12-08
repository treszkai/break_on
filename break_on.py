# TODO write or generate get-set-del_property()
# TODO property of a parent class
# TODO attribute of the instance type or of a parent class

from contextlib import contextmanager
from typing import Union, Container, Literal, Callable, Tuple, Any, Optional
from unittest.mock import patch, Mock

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
def set_attribute(cls: type, attr_name: str, hook=breakpoint):
    # Mock cls.__setattr__ such that
    #  - if it's called with prop_name, then it calls the hook first, and then
    #  - regardless of prop_name, it calls the saved_setattr
    saved_setattr = cls.__setattr__

    def __setattr__(self, name, value):
        if name == attr_name:
            hook(self, value)
        # Unlike `self.__dict__[name] = value`, the following works
        #  whether self."name" is an attribute or not
        saved_setattr(self, name, value)

    with patch.object(cls, '__setattr__', __setattr__):
        # TODO can we yield anything meaningful here?
        yield None


def is_property(cls: type, name: str):
    """True iff name is a property of class"""
    # TODO this probably fails for an inherited property
    try:
        return isinstance(cls.__dict__[name], property)
    except KeyError:
        # we could call is_property recursively, returning False if cls is type
        return False


@contextmanager
def set(
    cls: type,
    name: str,
    hook: Optional[Callable[[Any, Any], None]] = None
):
    """Context manager for hooking on to the setting of a property or attribute

    :param cls: Class whose property/attribute setter we are hooking on to
    :param name: Property/attribute name whose setter we are hooking on to
    :param hook: Hook to call when setting the parameter.
        Default: a new Mock instance.
    :return: A runtime context
    """
    # TODO should I care that this set shadows the built-in name set?

    if hook is None:
        hook = Mock()

    if is_property(cls, name):
        with set_property(cls, name, hook):
            yield hook
    else:
        with set_attribute(cls, name, hook):
            # TODO change this to `as mock; yield mock`
            yield hook
