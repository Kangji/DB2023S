from unittest import TestCase

from datatype import Column, ForeignKey, Record
from db import DbApi


class MockDb(dict):
    def __init__(self):
        super().__init__()

    def put(self, key: bytes, value: bytes):
        self[key] = value

    def get(self, key: bytes):
        try:
            return self[key]
        except KeyError:
            pass

    def delete(self, key: bytes):
        try:
            del self[key]
        except KeyError:
            pass


class MockDbApi(DbApi):
    def __init__(self):
        object().__init__()
        self.db = MockDb()
        self.db.put(b'_table_names', b'[]')

    def __del__(self):
        pass


class TestDbApi(TestCase):
    EMPTY = {b'_table_names': b'[]'}
    FOO = {
        b'_table_names': b'["foo"]',
        b'_foo_col_name_idx': b'{"id": 0}',
        b'_foo_cols': b'[{"name": "id", "type": "int", "null": "N", "key": "PRI/FOR"}]',
        b'_foo_pk': b'["id"]',
        b'_foo_fks': b'[{"fk": ["id"], "ref_table": "foo"}]',
        b'_foo_ref_cnt': b'0',
        b'_foo_rec_counter': b'0',
        b'_foo_rec_idx': b'[]',
    }
    FOOBAR = {
        b'_table_names': b'["foo", "bar"]',
        b'_foo_col_name_idx': b'{"id": 0}',
        b'_foo_cols': b'[{"name": "id", "type": "int", "null": "N", "key": "PRI/FOR"}]',
        b'_foo_pk': b'["id"]',
        b'_foo_fks': b'[{"fk": ["id"], "ref_table": "foo"}]',
        b'_foo_ref_cnt': b'1',
        b'_foo_rec_counter': b'0',
        b'_foo_rec_idx': b'[]',
        b'_bar_col_name_idx': b'{"id": 0}',
        b'_bar_cols': b'[{"name": "id", "type": "int", "null": "Y", "key": "FOR"}]',
        b'_bar_pk': b'[]',
        b'_bar_fks': b'[{"fk": ["id"], "ref_table": "foo"}]',
        b'_bar_ref_cnt': b'0',
        b'_bar_rec_counter': b'0',
        b'_bar_rec_idx': b'[]'
    }
    FOORECS = {
        b'_table_names': b'["foo"]',
        b'_foo_col_name_idx': b'{"id": 0}',
        b'_foo_cols': b'[{"name": "id", "type": "int", "null": "N", "key": "PRI/FOR"}]',
        b'_foo_pk': b'["id"]',
        b'_foo_fks': b'[{"fk": ["id"], "ref_table": "foo"}]',
        b'_foo_ref_cnt': b'0',
        b'_foo_rec_counter': b'4',
        b'_foo_rec_idx': b'[1, 3]',
        b'_foo_1': b'{"id": 3}',
        b'_foo_3': b'{"id": 4}'
    }

    def test_table_api(self):
        db = MockDbApi()

        # Create foo
        foo_cols = [Column.from_dict({'name': 'id', 'type': 'int', 'null': 'N', 'key': 'PRI/FOR'})]
        foo_pk = ['id']
        foo_fks = [ForeignKey.from_dict({'fk': ['id'], 'ref_table': 'foo'})]
        db.create_table('foo', foo_cols, foo_pk, foo_fks)

        assert ['foo'] == db.table_names()
        assert {'id': 0} == db.col_name_idx('foo')
        assert foo_cols == db.cols('foo')
        assert foo_pk == db.pk('foo')
        assert foo_fks == db.fks('foo')
        assert 0 == db.ref_cnt('foo')
        assert [] == db.rec_idx('foo')
        assert self.FOO == dict(db.db)

        # Create bar
        bar_cols = [Column.from_dict({'name': 'id', 'type': 'int', 'null': 'Y', 'key': 'FOR'})]
        bar_pk = []
        bar_fks = [ForeignKey.from_dict({'fk': ['id'], 'ref_table': 'foo'})]
        db.create_table('bar', bar_cols, bar_pk, bar_fks)

        assert ['foo', 'bar'] == db.table_names()
        assert {'id': 0} == db.col_name_idx('bar')
        assert bar_cols == db.cols('bar')
        assert bar_pk == db.pk('bar')
        assert bar_fks == db.fks('bar')
        assert 1 == db.ref_cnt('foo')
        assert 0 == db.ref_cnt('bar')
        assert [] == db.rec_idx('bar')
        assert self.FOOBAR == dict(db.db)

        # Drop bar
        db.drop_table('bar')

        assert ['foo'] == db.table_names()
        assert {'id': 0} == db.col_name_idx('foo')
        assert foo_cols == db.cols('foo')
        assert foo_pk == db.pk('foo')
        assert foo_fks == db.fks('foo')
        assert 0 == db.ref_cnt('foo')
        assert [] == db.rec_idx('foo')
        assert self.FOO == dict(db.db)

        # Drop foo
        db.drop_table('foo')
        assert [] == db.table_names()
        assert self.EMPTY == dict(db.db)

    def test_record_api(self):
        db = MockDbApi()

        # Create foo
        cols = [Column.from_dict({'name': 'id', 'type': 'int', 'null': 'N', 'key': 'PRI/FOR'})]
        pk = ['id']
        fks = [ForeignKey.from_dict({'fk': ['id'], 'ref_table': 'foo'})]
        db.create_table('foo', cols, pk, fks)

        # Insert record - 1
        record1 = Record.from_dict('foo', {'id': 1})
        db.insert_record(record1)

        assert [0] == db.rec_idx('foo')
        assert [(0, record1)] == db.select_all_records('foo')

        # Insert record - 3
        record2 = Record.from_dict('foo', {'id': 3})
        db.insert_record(record2)

        assert [0, 1] == db.rec_idx('foo')
        assert [(0, record1), (1, record2)] == db.select_all_records('foo')

        # Insert record - 2
        record3 = Record.from_dict('foo', {'id': 2})
        db.insert_record(record3)

        assert [0, 1, 2] == db.rec_idx('foo')
        assert [(0, record1), (1, record2), (2, record3)] == db.select_all_records('foo')

        # Delete record - 1, 2
        db.delete_records('foo', [0, 2])

        assert [1] == db.rec_idx('foo')
        assert [(1, record2)] == db.select_all_records('foo')

        # Insert record - 4
        record4 = Record.from_dict('foo', {'id': 4})
        db.insert_record(record4)

        assert [1, 3] == db.rec_idx('foo')
        assert [(1, record2), (3, record4)] == db.select_all_records('foo')
        assert self.FOORECS == dict(db.db)
