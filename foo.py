# test that if another module imports foo.py and creates an instance of Foo(),
#  then that wouldn't be patched


class Foo:
    my_attr = 2

    def set_my_attr(self, value):
        self.my_attr = value

    @property
    def my_prop(self):
        return self.my_attr

    @my_prop.setter
    def my_prop(self, value):
        self.my_attr = value


def some_func():
    x = Foo()
    x.set_my_attr(2)
    x.my_attr = 3
    x.my_prop = 5