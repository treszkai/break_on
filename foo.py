# test that if another module imports foo.py and creates an instance of Foo(),
#  then that wouldn't be patched


class Foo:
    my_attr = 2

    def set_my_attr(self, value):
        self.my_attr = value

    @property
    def my_prop(self):
        return self._my_prop

    @my_prop.setter
    def my_prop(self, value):
        self._my_prop = value


def some_func():
    x = Foo()
    x.set_my_attr(2)
    x.my_attr = 3
    x.my_prop = 5