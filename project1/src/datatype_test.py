from unittest import TestCase

from datatype import Column, ForeignKey, date, CompOp, boolean, Row, TableColumn, Record
from error import SqlSyntaxError, WhereColumnNotExist, WhereAmbiguousReference, WhereTableNotSpecified
from util import ExpectException


####################################################################################################
# Value
####################################################################################################

class TestDate(TestCase):
    def test_date(self):
        d = date(2023, 1, 1)
        value = {'year': 2023, 'month': 1, 'day': 1}
        assert value == dict(d)

    def test_from_dict(self):
        d = date.from_dict({'year': 2023, 'month': 1, 'day': 1})
        assert d == date(2023, 1, 1)

    def test_fromisoformat(self):
        d = date(2023, 1, 1)
        assert d == date.fromisoformat('2023-01-01')

    @ExpectException(SqlSyntaxError)
    def test_fromisoformat_fail(self):
        date.fromisoformat('9999-99-99')

    def test_comp(self):
        d0 = date.fromisoformat('2023-02-10')

        d1 = date.fromisoformat('2023-02-10')
        assert d0 == d1
        assert not d0 != d1
        assert not d0 < d1
        assert d0 <= d1
        assert not d0 > d1
        assert d0 >= d1

        d1 = date.fromisoformat('2023-02-20')
        assert not d0 == d1
        assert d0 != d1
        assert d0 < d1
        assert d0 <= d1
        assert not d0 > d1
        assert not d0 >= d1

        d1 = date.fromisoformat('2023-03-10')
        assert not d0 == d1
        assert d0 != d1
        assert d0 < d1
        assert d0 <= d1
        assert not d0 > d1
        assert not d0 >= d1

        d1 = date.fromisoformat('2024-02-10')
        assert not d0 == d1
        assert d0 != d1
        assert d0 < d1
        assert d0 <= d1
        assert not d0 > d1
        assert not d0 >= d1

        d1 = date.fromisoformat('2023-02-02')
        assert not d0 == d1
        assert d0 != d1
        assert not d0 < d1
        assert not d0 <= d1
        assert d0 > d1
        assert d0 >= d1

        d1 = date.fromisoformat('2023-01-10')
        assert not d0 == d1
        assert d0 != d1
        assert not d0 < d1
        assert not d0 <= d1
        assert d0 > d1
        assert d0 >= d1

        d1 = date.fromisoformat('2022-02-10')
        assert not d0 == d1
        assert d0 != d1
        assert not d0 < d1
        assert not d0 <= d1
        assert d0 > d1
        assert d0 >= d1


class TestBoolean(TestCase):
    def test_bool(self):
        assert boolean.true
        assert not boolean.false
        assert not boolean.unknown

    def test_and(self):
        assert (boolean.true & boolean.true) is boolean.true
        assert (boolean.true & boolean.unknown) is boolean.unknown
        assert (boolean.true & boolean.false) is boolean.false
        assert (boolean.unknown & boolean.true) is boolean.unknown
        assert (boolean.unknown & boolean.unknown) is boolean.unknown
        assert (boolean.unknown & boolean.false) is boolean.false
        assert (boolean.false & boolean.true) is boolean.false
        assert (boolean.false & boolean.unknown) is boolean.false
        assert (boolean.false & boolean.false) is boolean.false

    def test_or(self):
        assert (boolean.true | boolean.true) is boolean.true
        assert (boolean.true | boolean.unknown) is boolean.true
        assert (boolean.true | boolean.false) is boolean.true
        assert (boolean.unknown | boolean.true) is boolean.true
        assert (boolean.unknown | boolean.unknown) is boolean.unknown
        assert (boolean.unknown | boolean.false) is boolean.unknown
        assert (boolean.false | boolean.true) is boolean.true
        assert (boolean.false | boolean.unknown) is boolean.unknown
        assert (boolean.false | boolean.false) is boolean.false

    def test_not(self):
        assert -boolean.true is boolean.false
        assert -boolean.unknown is boolean.unknown
        assert -boolean.false is boolean.true


class TestCompOp(TestCase):
    # noinspection DuplicatedCode
    def test(self):
        i1 = 3
        i2 = 4
        s1 = 'a'
        s2 = 'b'
        d1 = date.fromisoformat('2022-01-01')
        d2 = date.fromisoformat('2022-01-02')
        n = None

        op = CompOp('<')
        assert op.eval(i1, n) is boolean.unknown
        assert op.eval(i1, i2) is boolean.true
        assert op.eval(i1, i1) is boolean.false
        assert op.eval(i2, i1) is boolean.false
        assert op.eval(n, i1) is boolean.unknown
        assert op.eval(s1, n) is boolean.unknown
        assert op.eval(s1, s2) is boolean.true
        assert op.eval(s1, s1) is boolean.false
        assert op.eval(s2, s1) is boolean.false
        assert op.eval(n, s1) is boolean.unknown
        assert op.eval(d1, n) is boolean.unknown
        assert op.eval(d1, d2) is boolean.true
        assert op.eval(d1, d1) is boolean.false
        assert op.eval(d2, d1) is boolean.false
        assert op.eval(n, d1) is boolean.unknown

        op = CompOp('>')
        assert op.eval(i1, n) is boolean.unknown
        assert op.eval(i1, i2) is boolean.false
        assert op.eval(i1, i1) is boolean.false
        assert op.eval(i2, i1) is boolean.true
        assert op.eval(n, i1) is boolean.unknown
        assert op.eval(s1, n) is boolean.unknown
        assert op.eval(s1, s2) is boolean.false
        assert op.eval(s1, s1) is boolean.false
        assert op.eval(s2, s1) is boolean.true
        assert op.eval(n, s1) is boolean.unknown
        assert op.eval(d1, n) is boolean.unknown
        assert op.eval(d1, d2) is boolean.false
        assert op.eval(d1, d1) is boolean.false
        assert op.eval(d2, d1) is boolean.true
        assert op.eval(n, d1) is boolean.unknown

        op = CompOp('<=')
        assert op.eval(i1, n) is boolean.unknown
        assert op.eval(i1, i2) is boolean.true
        assert op.eval(i1, i1) is boolean.true
        assert op.eval(i2, i1) is boolean.false
        assert op.eval(n, i1) is boolean.unknown
        assert op.eval(s1, n) is boolean.unknown
        assert op.eval(s1, s2) is boolean.true
        assert op.eval(s1, s1) is boolean.true
        assert op.eval(s2, s1) is boolean.false
        assert op.eval(n, s1) is boolean.unknown
        assert op.eval(d1, n) is boolean.unknown
        assert op.eval(d1, d2) is boolean.true
        assert op.eval(d1, d1) is boolean.true
        assert op.eval(d2, d1) is boolean.false
        assert op.eval(n, d1) is boolean.unknown

        op = CompOp('>=')
        assert op.eval(i1, n) is boolean.unknown
        assert op.eval(i1, i2) is boolean.false
        assert op.eval(i1, i1) is boolean.true
        assert op.eval(i2, i1) is boolean.true
        assert op.eval(n, i1) is boolean.unknown
        assert op.eval(s1, n) is boolean.unknown
        assert op.eval(s1, s2) is boolean.false
        assert op.eval(s1, s1) is boolean.true
        assert op.eval(s2, s1) is boolean.true
        assert op.eval(n, s1) is boolean.unknown
        assert op.eval(d1, n) is boolean.unknown
        assert op.eval(d1, d2) is boolean.false
        assert op.eval(d1, d1) is boolean.true
        assert op.eval(d2, d1) is boolean.true
        assert op.eval(n, d1) is boolean.unknown

        op = CompOp('=')
        assert op.eval(i1, n) is boolean.unknown
        assert op.eval(i1, i2) is boolean.false
        assert op.eval(i1, i1) is boolean.true
        assert op.eval(i2, i1) is boolean.false
        assert op.eval(n, i1) is boolean.unknown
        assert op.eval(s1, n) is boolean.unknown
        assert op.eval(s1, s2) is boolean.false
        assert op.eval(s1, s1) is boolean.true
        assert op.eval(s2, s1) is boolean.false
        assert op.eval(n, s1) is boolean.unknown
        assert op.eval(d1, n) is boolean.unknown
        assert op.eval(d1, d2) is boolean.false
        assert op.eval(d1, d1) is boolean.true
        assert op.eval(d2, d1) is boolean.false
        assert op.eval(n, d1) is boolean.unknown

        op = CompOp('!=')
        assert op.eval(i1, n) is boolean.unknown
        assert op.eval(i1, i2) is boolean.true
        assert op.eval(i1, i1) is boolean.false
        assert op.eval(i2, i1) is boolean.true
        assert op.eval(n, i1) is boolean.unknown
        assert op.eval(s1, n) is boolean.unknown
        assert op.eval(s1, s2) is boolean.true
        assert op.eval(s1, s1) is boolean.false
        assert op.eval(s2, s1) is boolean.true
        assert op.eval(n, s1) is boolean.unknown
        assert op.eval(d1, n) is boolean.unknown
        assert op.eval(d1, d2) is boolean.true
        assert op.eval(d1, d1) is boolean.false
        assert op.eval(d2, d1) is boolean.true
        assert op.eval(n, d1) is boolean.unknown


####################################################################################################
# Metadata
####################################################################################################

class TestForeignKey(TestCase):
    def test(self):
        fk = ForeignKey(['id'], 'foo')
        value = {'fk': ['id'], 'ref_table': 'foo'}
        assert value == fk

    def test_from_dict(self):
        fk = ForeignKey(['id'], 'foo')
        value = {'fk': ['id'], 'ref_table': 'foo'}
        assert ForeignKey.from_dict(value) == fk


class TestColumn(TestCase):
    def test(self):
        col = Column('id', Column.Type.INT)
        value = {'name': 'id', 'type': 'int', 'null': 'Y', 'key': ''}
        assert value == col

        col.add_fk()
        value['key'] = 'FOR'
        assert value == col

        col.add_pk()
        value['key'] = 'PRI/FOR'
        assert value == col

        col.set_not_null()
        value['null'] = 'N'
        assert value == col

    def test_from_dict(self):
        col = Column('id', Column.Type.CHAR, 10)
        value = {'name': 'id', 'type': {'length': 10}, 'null': 'Y', 'key': ''}
        assert value == col
        assert Column.from_dict(value) == col


####################################################################################################
# Identifier
####################################################################################################

class TestTableColumn(TestCase):
    def test(self):
        col = TableColumn('id', table_name='foo')
        assert str(col) == 'foo.id'
        assert f'{col}' == 'foo.id'

        col = TableColumn('id')
        assert str(col) == 'id'
        assert f'{col}' == 'id'


####################################################################################################
# Data
####################################################################################################

class TestRecord(TestCase):
    def test_from_dict(self):
        record = Record.from_dict('foo', {'id': 3, 'name': 'Jiho'})
        assert record == {'id': 3, 'name': 'Jiho'}


class TestRow(TestCase):
    def test_from_dict(self):
        row = Row.from_dict({'id': {'foo': 3}, 'name': {'foo': 'Jiho'}})
        assert row == {'id': {'foo': 3}, 'name': {'foo': 'Jiho'}}

    def test_from_record(self):
        row = Row.from_record(Record.from_dict('foo', {'id': 3, 'name': 'Jiho'}))
        assert row == {'id': {'foo': 3}, 'name': {'foo': 'Jiho'}}

    def test_merge(self):
        left = Row.from_record(Record.from_dict('foo', {'id': 3, 'name': 'Jiho'}))
        right = Row.from_record(Record.from_dict('bar', {'id': 4, 'city': 'Seoul'}))
        assert Row.merge(left, right) == {'id': {'foo': 3, 'bar': 4}, 'name': {'foo': 'Jiho'}, 'city': {'bar': 'Seoul'}}

    def test_search_success(self):
        row = Row()
        row.add_value('id', 'foo', 3)
        row.add_value('id', 'bar', 4)
        row.add_value('name', 'foo', 'Jiho')
        assert row.search(TableColumn('id', table_name='foo')) == 3
        assert row.search(TableColumn('id', table_name='bar')) == 4
        assert row.search(TableColumn('name')) == 'Jiho'

    @ExpectException(WhereTableNotSpecified)
    def test_table_not_specified(self):
        row = Row()
        row.add_value('id', 'foo', 3)
        row.search(TableColumn('id', table_name='bar'))

    @ExpectException(WhereColumnNotExist)
    def test_column_not_exist1(self):
        Row().search(TableColumn('id'))

    @ExpectException(WhereColumnNotExist)
    def test_column_not_exist2(self):
        row = Row()
        row.add_value('id', 'foo', 3)
        row.add_value('name', 'bar', 'jiho')
        row.search(TableColumn('id', 'bar'))

    @ExpectException(WhereAmbiguousReference)
    def test_ambiguous_reference(self):
        row = Row()
        row.add_value('id', 'foo', 3)
        row.add_value('id', 'bar', 4)
        row.search(TableColumn('id'))
