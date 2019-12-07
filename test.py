import unittest
from unittest.mock import patch, PropertyMock, Mock, call

from foo import Foo, some_func


class MyTestCase(unittest.TestCase):
    def test_property_mock(self):
        # PropertyMock only works if you set the value of the attribute manually
        #  for each call (or all of them)

        original_foo = Foo()
        self.assertNotIn(
            'my_attr',
            original_foo.__dict__,
            '“my_attr” is not yet in the original Foo instance’s dictionary.'
        )
        self.assertIn(
            'my_attr',
            Foo.__dict__,
            '“my_attr” is in the original Foo class’s dictionary.'
         )

        original_foo.set_my_attr(13)
        self.assertIn(
            'my_attr',
            original_foo.__dict__,
            '“my_attr” is now in the original Foo instance’s dictionary.'
        )

        with patch.object(Foo, 'my_attr', new_callable=PropertyMock) as mocked_attr:
            # Foo.my_attr is a Mock instance, but not a PropertyMock
            self.assertIsInstance(Foo.my_attr, Mock)
            self.assertNotIsInstance(Foo.my_attr, PropertyMock)
            mocked_attr.return_value = 4
            foo = Foo()
            foo.my_attr = -27

            self.assertNotIn(
                'my_attr',
                foo.__dict__,
                '“my_attr” is not in the instance’s dictionary.'
            )

            self.assertEqual(4, foo.my_attr)

            # This one I don’t understand. I guess it’s still a Mock,
            #  but __get__ is called even on the class attribute access.
            #  But then how do I access the Mock instance through the Foo class?
            self.assertEqual(4, Foo.my_attr)
            self.assertNotIsInstance(Foo.my_attr, Mock)

        self.assertEqual(
            [
                call(),  # Foo.my_attr
                call(),  # Foo.my_attr
                call(-27),  # foo.my_attr = -27
                call(),  # assertEqual(4, foo.my_attr)
                call(),  # Foo.my_attr
                call(),  # same
            ],
            mocked_attr.mock_calls
        )

    def test_mock_property_write(self):
        # I want to mock a property in a way that setting it will
        #  call the original property's __set__,
        # and accessing it will call the original property's __get__.
        # So I'm just writing a wrapper around __get__ and __set__.

        # original_property: property = Foo.my_prop
        # def get(obj):
        #     return original_property.__get__(obj, type(obj))
        # def set(obj, value):
        #     breakpoint()
        #     return original_property.__set__(obj, value)
        # mocked_property = property(fget=get, fset=set)

        class MyPropertyMock(property):
            def __init__(property_self, owner, prop_name):
                assert isinstance(owner, type), "“owner” argument must be a type"
                property_self.__orig_prop = getattr(owner, prop_name)
            def __get__(property_self, instance, owner):
                return property_self.__orig_prop.__get__(instance, owner)
            def __set__(property_self, instance, value):
                breakpoint()
                return property_self.__orig_prop.__set__(instance, value)

        self.assertIsInstance(Foo.my_prop, property)

        # TODO is this affected by the patch?
        original_foo = Foo()

        # TODO make a context manager for this?
        with patch.object(Foo, 'my_prop', new=MyPropertyMock(Foo, 'my_prop')):
            self.assertIsInstance(Foo.my_prop, property)

            foo = Foo()
            foo.my_prop = 4
            self.assertEqual(foo.my_prop, 4)

        self.assertEqual(
            foo.my_prop,
            4,
            'Because we set the original property, the value is '
                'preserved outside the patch context'
        )

    def test_mock_either(self):
        def is_attribute(obj, name):
            """Return True iff name is an attribute of obj"""
            return name in obj.__dict__

if __name__ == '__main__':
    unittest.main()