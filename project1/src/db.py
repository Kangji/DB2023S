from typing import Optional, List, Dict, Tuple

from berkeleydb import db

from datatype import Column, Key, ForeignKey, Record, date
from util import Bytes


class DbApi:
    """
    Customized BerkeleyDB API.

    All data and metadata are stored in single file.
    Keys for metadatas starts with underscore followed by table name followed by underscore followed by matadata type.
    Keys for the records starts with underscore followed by table name followed by underscore followed by record index.
    Note that both are not valid identifiers.

    Arguments for the API are not validated here. It must be checked on higher abstraction.
    """

    def __init__(self, filename: str):
        self.db = db.DB()
        try:
            with open(filename):
                self.db.open(filename, dbtype=db.DB_HASH)
        except FileNotFoundError:
            self.db.open(filename, dbtype=db.DB_HASH, flags=db.DB_CREATE)
            self.db.put(self.__key_table_names(), b'[]')

    def __del__(self):
        self.db.close()

    ################################################################################################
    # Internal key generators
    ################################################################################################

    @staticmethod
    def __key_table_names() -> bytes:
        return b'_table_names'

    @staticmethod
    def __key_col_name_idx(table_name: str) -> bytes:
        return Bytes.from_str(f'_{table_name}_col_name_idx')

    @staticmethod
    def __key_cols(table_name: str) -> bytes:
        return Bytes.from_str(f'_{table_name}_cols')

    @staticmethod
    def __key_pk(table_name: str) -> bytes:
        return Bytes.from_str(f'_{table_name}_pk')

    @staticmethod
    def __key_fks(table_name: str) -> bytes:
        return Bytes.from_str(f'_{table_name}_fks')

    @staticmethod
    def __key_ref_cnt(table_name: str) -> bytes:
        return Bytes.from_str(f'_{table_name}_ref_cnt')

    @staticmethod
    def __key_rec_counter(table_name: str) -> bytes:
        return Bytes.from_str(f'_{table_name}_rec_counter')

    @staticmethod
    def __key_rec_idx(table_name: str) -> bytes:
        return Bytes.from_str(f'_{table_name}_rec_idx')

    @staticmethod
    def __key_rec(table_name: str, idx: int) -> bytes:
        return Bytes.from_str(f'_{table_name}_{idx}')

    ################################################################################################
    # Table Metadata Operations
    ################################################################################################

    def table_names(self) -> List[str]:
        return Bytes.to_obj(self.db.get(self.__key_table_names()))

    def __add_table_name(self, table_name: str):
        table_names = self.table_names()
        table_names.append(table_name)
        self.db.put(self.__key_table_names(), Bytes.from_obj(table_names))

    def __rm_table_name(self, table_name: str):
        table_names = self.table_names()
        table_names.remove(table_name)
        self.db.put(self.__key_table_names(), Bytes.from_obj(table_names))

    def col_name_idx(self, table_name: str) -> Optional[Dict[str, int]]:
        return Bytes.to_obj(self.db.get(self.__key_col_name_idx(table_name)))

    def cols(self, table_name: str) -> Optional[List[Column]]:
        cols = Bytes.to_obj(self.db.get(self.__key_cols(table_name)))
        if cols is not None:
            return [Column.from_dict(col) for col in cols]

    def pk(self, table_name: str) -> Optional[Key]:
        return Bytes.to_obj(self.db.get(self.__key_pk(table_name)))

    def fks(self, table_name: str) -> Optional[List[ForeignKey]]:
        fks = Bytes.to_obj(self.db.get(self.__key_fks(table_name)))
        if fks is not None:
            return [ForeignKey.from_dict(fk) for fk in fks]

    def ref_cnt(self, table_name: str) -> Optional[int]:
        return Bytes.to_int(self.db.get(self.__key_ref_cnt(table_name)))

    def __update_ref_cnt(self, table_name: str, delta: int):
        ref_cnt = self.ref_cnt(table_name) + delta
        self.db.put(self.__key_ref_cnt(table_name), Bytes.from_int(ref_cnt))

    def __incr_ref_cnt(self, table_name: str):
        self.__update_ref_cnt(table_name, 1)

    def __decr_ref_cnt(self, table_name: str):
        self.__update_ref_cnt(table_name, -1)

    ################################################################################################
    # Record Metadata Operations
    ################################################################################################

    def __fetch_add_rec_counter(self, table_name: str) -> int:
        key_rec_counter = self.__key_rec_counter(table_name)
        rec_counter = Bytes.to_int(self.db.get(key_rec_counter))
        self.db.put(key_rec_counter, Bytes.from_int(rec_counter + 1))
        return rec_counter

    def rec_idx(self, table_name: str) -> Optional[List[int]]:
        return Bytes.to_obj(self.db.get(self.__key_rec_idx(table_name)))

    def __insert_rec_idx(self, table_name: str, idx: int):
        rec_idx = self.rec_idx(table_name)
        rec_idx.append(idx)
        self.db.put(self.__key_rec_idx(table_name), Bytes.from_obj(rec_idx))

    def __delete_rec_idx(self, table_name: str, idx_to_delete: List[int]):
        rec_idx = list(filter(lambda idx: idx not in idx_to_delete, self.rec_idx(table_name)))
        self.db.put(self.__key_rec_idx(table_name), Bytes.from_obj(rec_idx))

    ################################################################################################
    # Table API
    ################################################################################################

    def create_table(self, table_name: str, cols: List[Column], pk: Key, fks: List[ForeignKey]):
        col_name_idx = dict((col.name, i) for i, col in enumerate(cols))

        # Create metadata
        self.__add_table_name(table_name)
        self.db.put(self.__key_col_name_idx(table_name), Bytes.from_obj(col_name_idx))
        self.db.put(self.__key_cols(table_name), Bytes.from_obj(cols))
        self.db.put(self.__key_pk(table_name), Bytes.from_obj(pk))
        self.db.put(self.__key_fks(table_name), Bytes.from_obj(fks))
        self.db.put(self.__key_ref_cnt(table_name), Bytes.from_int(0))
        self.db.put(self.__key_rec_counter(table_name), Bytes.from_int(0))
        self.db.put(self.__key_rec_idx(table_name), Bytes.from_obj([]))

        # Increment ref cnt
        for fk in fks:
            if fk.ref_table != table_name:
                self.__incr_ref_cnt(fk.ref_table)

    def drop_table(self, table_name: str):
        # Delete records
        for idx in self.rec_idx(table_name):
            self.db.delete(self.__key_rec(table_name, idx))

        # Decrement ref cnt
        for fk in self.fks(table_name):
            if fk.ref_table != table_name:
                self.__decr_ref_cnt(fk.ref_table)

        # Delete metadata
        self.db.delete(self.__key_rec_idx(table_name))
        self.db.delete(self.__key_rec_counter(table_name))
        self.db.delete(self.__key_ref_cnt(table_name))
        self.db.delete(self.__key_fks(table_name))
        self.db.delete(self.__key_pk(table_name))
        self.db.delete(self.__key_cols(table_name))
        self.db.delete(self.__key_col_name_idx(table_name))
        self.__rm_table_name(table_name)

    ################################################################################################
    # Record API
    ################################################################################################

    def insert_record(self, record: Record):
        table_name = record.table_name
        idx = self.__fetch_add_rec_counter(table_name)

        self.db.put(self.__key_rec(table_name, idx), Bytes.from_obj(record))
        self.__insert_rec_idx(table_name, idx)

    def delete_records(self, table_name: str, idx_to_delete: List[int]):
        self.__delete_rec_idx(table_name, idx_to_delete)
        for idx in idx_to_delete:
            self.db.delete(self.__key_rec(table_name, idx))

    def select_all_records(self, table_name: str) -> Optional[List[Tuple[int, Record]]]:
        rec_idx = self.rec_idx(table_name)
        if rec_idx is not None:
            return [(idx, self.__select_record(table_name, idx)) for idx in rec_idx]

    def __select_record(self, table_name, idx: int) -> Optional[Record]:
        record = Bytes.to_obj(self.db.get(self.__key_rec(table_name, idx)))
        if record is not None:
            for col_name in record:
                if isinstance(record[col_name], dict):  # date
                    record[col_name] = date.from_dict(record[col_name])

            return Record.from_dict(table_name, record)
