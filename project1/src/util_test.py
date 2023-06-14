from unittest import TestCase

from util import Bytes, ExpectException, Padding


class TestPadding(TestCase):
    def test_padding(self):
        assert '===3===' == Padding(7, fill='=', align='^').apply_to(3)
        assert 'hello   ' == Padding(8).apply_to('hello')
        assert 'xxbye' == Padding(5, fill='x', align='>').apply_to('bye')


class TestExpectException(TestCase):
    class Foo(BaseException):
        ...

    @ExpectException(BaseException)
    def test_fail(self):
        raise self.Foo()


class TestBytes(TestCase):
    def test_conversion(self):
        s = 'hello'
        bs = b'hello'
        n = 3
        bn = b'3'
        obj1 = {'x': 3}
        bobj1 = b'{"x": 3}'
        obj2 = ['x', {'x': 3}]
        bobj2 = b'["x", {"x": 3}]'
        assert bs == Bytes.from_str(s)
        assert None is Bytes.from_str(None)

        assert bn == Bytes.from_int(n)
        assert None is Bytes.from_int(None)

        assert bobj1 == Bytes.from_obj(obj1)
        assert None is Bytes.from_obj(None)

        assert bobj2 == Bytes.from_obj(obj2)
        assert None is Bytes.from_obj(None)

        assert s == Bytes.to_str(bs)
        assert None is Bytes.to_str(None)

        assert n == Bytes.to_int(bn)
        assert None is Bytes.to_int(None)

        assert obj1 == Bytes.to_obj(bobj1)
        assert None is Bytes.to_obj(None)

        assert obj2 == Bytes.to_obj(bobj2)
        assert None is Bytes.to_obj(None)
