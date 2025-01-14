Set a breakpoint on the setting or getting of a property or attribute.

```python
import break_on

foo = Foo()

with break_on.set(Foo, 'my_attr'):  # or 'my_prop' for setting the property
    foo.my_attr = 53  # breakpoint hit

with break_on.get(Foo, 'my_attr'):
    assert foo.my_attr == 53  # breakpoint hit
```

#### invisipatch.py

It does something similar but in a different manner. Tbh I don't remember the differences. 

Usage for setting a breakpoint:

```python
import invisipatch

with invisipatch.setattr(Foo, 'my_prop', hook=invisipatch.BREAKPOINT):
    foo = Foo()
    foo.my_prop = 7  # breakpoint hit
```

Or just mock the underlying property/attribute:

```python
import invisipatch

with invisipatch.setattr(Foo, 'my_prop', hook=mock) as mock_prop:
    foo = Foo()
    foo.my_prop = 7
    assert 7 == foo.my_prop

    mock_prop.assert_has_calls([foo, 7])
```

## Packaging

No packaging, use as a standalone module.
