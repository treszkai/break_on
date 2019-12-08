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


class SubFoo(Foo):
    pass
