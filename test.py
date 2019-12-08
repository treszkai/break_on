import unittest
from collections import namedtuple
from unittest.mock import patch, PropertyMock, Mock, call

import break_on
from break_on import MyPropertyMock
from foo import Foo


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

        self.assertIsInstance(Foo.my_prop, property)

        # TODO is this affected by the patch?
        original_foo = Foo()

        mock = Mock()
        with break_on.set_property(Foo, 'my_prop', hook=mock):
            self.assertIsInstance(Foo.my_prop, property)
            foo = Foo()
            foo.my_prop = 4
            self.assertEqual(foo.my_prop, 4)
            mock.assert_called_once_with(foo, 4)

        self.assertEqual(
            foo.my_prop,
            4,
            'Because we set the original property, the value is '
                'preserved outside the patch context'
        )

    def test_mock_attribute_write(self):
        original_foo = Foo()
        self.assertIsIn('my_attr', original_foo.__dict__)
        original_attr_value = original_foo.my_attr

        with break_on.set_attribute(Foo, 'my_attr'):
            foo = Foo()
            self.assertIn('my_attr', foo.__dict__)
            self.assertEqual(original_attr_value, foo.my_attr)
            foo.my_attr = 3
            self.assertEqual(3, foo.my_attr)

    def test_cannot_patch_frozen_attribute(self):
        NT = namedtuple('NT', ('a', 'b'))
        nt = NT(3, 4)
        with self.assertRaises(
                AttributeError,
                'mock.patch can’t mock a frozen attribute either'
        ):
            with patch.object(nt, "a"):
                pass

        with self.assertRaises(
                AttributeError,
                'mock.patch can’t mock a non-existent attribute of a frozen class'
        ):
            with patch.object(nt, "x"):
                pass

    def test_mock_either(self):
        raise NotImplementedError

        def is_attribute(obj, name):
            """Return True iff name is an attribute of obj"""
            return name in obj.__dict__

if __name__ == '__main__':
    unittest.main()
