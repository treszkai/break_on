

import pdb
from contextlib import contextmanager
from typing import Literal
from unittest.mock import patch, Mock

BREAKPOINT = object()
MOCK = object()


@contextmanager
def set(
    cls: type,
    attr_name: str,
    action: Literal[BREAKPOINT, MOCK] = BREAKPOINT,
):
    """Context manager for setting a breakpoint to the setting of a property or attribute

    :param cls: Class whose property/attribute setter we are hooking on to
    :param name: Property/attribute name whose setter we are hooking on to
    :return: A runtime context, where __enter__ returns a Mock instance,
        which is called with *(instance, name, value).
    """
    saved_setattr = cls.__setattr__

    if action is BREAKPOINT:
        def __setattr__(self, name, value):
            if name == attr_name:
                breakpoint()
                # pdb.Pdb(skip=['break_on', 'contextlib', 'unittest.mock']).set_trace()
            # Unlike `self.__dict__[name] = value`, the following works
            #  whether self."name" is an attribute or not
            saved_setattr(self, name, value)

        with patch.object(cls, '__setattr__', __setattr__):
            yield None
    elif action is MOCK:
        mock = Mock()

        def __setattr__(self, name, value):
            if name == attr_name:
                mock(self, name, value)
            saved_setattr(self, name, value)

        with patch.object(cls, '__setattr__', __setattr__):
            yield mock
    else:
        raise ValueError("action argument must be either BREAKPOINT or MOCK")


def set_decorator(attr_name: str):
    def actual_decorator(cls: type):
        saved_setattr = cls.__setattr__

        def __setattr__(self, name, value):
            if name == attr_name:
                breakpoint()
            saved_setattr(self, name, value)

        return type(
            cls.__name__ + "BreakOnSet",
            (cls, ),
            {
                '__setattr__': __setattr__
            }
        )
    return actual_decorator


@contextmanager
def get(
    cls: type,
    attr_name: str,
    action: Literal[BREAKPOINT, MOCK] = BREAKPOINT
):
    """Context manager for setting a breakpoint to the getting of a property or attribute

    :param cls: Class whose property/attribute getter we are hooking on to
    :param name: Property/attribute name whose setter we are hooking on to
    :return: A runtime context
    """
    saved_getattribute = cls.__getattribute__

    if action is BREAKPOINT:
        def __getattribute__(self, name):
            if name == attr_name:
                breakpoint()
            saved_getattribute(self, name)

        with patch.object(cls, '__getattribute__', __getattribute__):
            yield None
    elif action is MOCK:
        mock = Mock()

        def __getattribute__(self, name):
            if name == attr_name:
                mock(self, name)
            saved_getattribute(self, name)

        with patch.object(cls, '__getattribute__', __getattribute__):
            if action is MOCK:
                yield mock
    else:
        raise ValueError("action argument must be either BREAKPOINT or MOCK")
