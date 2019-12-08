# TODO write or generate get-set-del_property()

from contextlib import contextmanager
from typing import Union, Container, Literal
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
        owner,
        prop_name,
        break_on: _BREAK_ON_OPTIONS = ALL
    ):
        assert isinstance(owner, type), "“owner” argument must be a type"
        if not isinstance(break_on, Container):
            self.break_on = {break_on}
        else:
            self.break_on = break_on
        # TODO should I specify a default?
        self.orig_prop = getattr(owner, prop_name)
        super().__init__()

    def __get__(self, instance, owner=None):
        if GET in self.break_on:
            breakpoint()
        return self.orig_prop.__get__(instance, owner)

    def __set__(self, instance, value):
        if SET in self.break_on:
            breakpoint()
        return self.orig_prop.__set__(instance, value)

    def __del__(self, instance):
        if DEL in self.break_on:
            breakpoint()
        return self.orig_prop.__del__(instance)


@contextmanager
def set_property(cls: type, prop_name: str):
    assert isinstance(cls, type), "“cls” argument must be a type"
    mocked_property = MyPropertyMock(cls, prop_name, break_on=SET)
    with patch.object(cls, prop_name, new=mocked_property):
        yield mocked_property


@contextmanager
def property_access(cls: type, prop_name: str, break_on: _BREAK_ON_OPTIONS):
    assert isinstance(cls, type), "“cls” argument must be a type"
    mocked_property = MyPropertyMock(cls, prop_name, break_on=break_on)
    with patch.object(cls, prop_name, new=mocked_property):
        yield mocked_property
