from enum import Enum
from functools import reduce
from typing import List, Optional, Tuple, Dict, Set, Union, Callable

from lark import Transformer, Token

from datatype import date, CompOp, Value, TableColumn, ForeignKey, Key, Column, boolean, Row, Predicate, Record
from db import DbApi
from error import *
from util import Print


def trivial(_: Row) -> boolean:
    return boolean.true


class TableElementTag(Enum):
    """Table element type tag (PK, FK or COL)."""

    PK = 0
    FK = 1
    COL = 2


# noinspection PyMethodMayBeStatic,PyUnusedLocal
class App(Transformer):
    """Interactive SQL application."""

    def __init__(self, db: DbApi):
        super().__init__()
        self.db = db

    ################################################################################################
    # Tokens
    ################################################################################################

    def INT(self, token: Token) -> int:
        return int(token)

    def STR(self, token: Token) -> str:
        return str(token[1:-1])  # remove quotes

    def DATE(self, token: Token) -> date:
        return date.fromisoformat(token)

    def IDENTIFIER(self, token: Token) -> str:
        return str(token.lower())  # case insensitive

    def NULL(self, token: Token) -> None:
        return None

    ################################################################################################
    # Operators
    ################################################################################################

    def LT(self, token: Token) -> CompOp:
        return CompOp.LT

    def GT(self, token: Token) -> CompOp:
        return CompOp.GT

    def LE(self, token: Token) -> CompOp:
        return CompOp.LE

    def GE(self, token: Token) -> CompOp:
        return CompOp.GE

    def EQ(self, token: Token) -> CompOp:
        return CompOp.EQ

    def NE(self, token: Token) -> CompOp:
        return CompOp.NE

    ################################################################################################
    # Common Rules
    ################################################################################################

    def table_name_list(self, items: List[str]) -> List[str]:
        return items  # list of table names

    def table_name(self, items: List[str]) -> str:
        return items[0]  # just identifier

    def column_name_list(self, items: List[str]) -> List[str]:
        return items[1:-1]  # remove parentheses

    def column_name(self, items: List[str]) -> str:
        return items[0]  # just identifier

    def table_column(self, items: List[Optional[str]]) -> TableColumn:
        table_name: Optional[str] = items[0]
        col_name: str = items[1]
        return TableColumn(col_name, table_name)

    def value_list(self, items: list) -> List[Value]:
        return items[1:-1]  # remove parenthesis

    def value(self, items: List[Value]) -> Value:
        return items[0]  # just single value

    def comp_op(self, items: List[CompOp]) -> CompOp:
        return items[0]  # just single comparison operator

    ################################################################################################
    # Where Clause (Returns lambda corresponding to the boolean expression)
    ################################################################################################

    def where_clause(self, items: list) -> Predicate:
        return items[1]  # remove 'WHERE' keyword

    def boolean_expr(self, items: List[Predicate]) -> Predicate:
        return lambda row: reduce(lambda b, f: b | f(row), items, boolean.false)  # disjunction of boolean terms

    def or_boolean_term(self, items: list) -> Predicate:
        return items[1]  # remove 'OR' keyword

    def boolean_term(self, items: List[Predicate]) -> Predicate:
        return lambda row: reduce(lambda b, f: b & f(row), items, boolean.true)  # conjunction of boolean factors

    def and_boolean_factor(self, items: list) -> Predicate:
        return items[1]  # remove 'AND' keyword

    def boolean_factor(self, items: list) -> Predicate:
        negate: bool = items[0] is not None
        boolean_test: Predicate = items[1]
        return lambda row: -boolean_test(row) if negate else boolean_test(row)  # (maybe) negate boolean test

    def boolean_test(self, items: List[Predicate]) -> Predicate:
        return items[0]  # parenthesized_boolean_expr or predicate

    def parenthesized_boolean_expr(self, items: list) -> Predicate:
        return items[1]  # remove parenthesis

    def predicate(self, items: List[Predicate]) -> Predicate:
        return items[0]  # comparison_predicate or null_predicate

    def comparison_predicate(self, items: list) -> Predicate:
        operand1: Callable[[Row], Value] = items[0]
        comp_op: CompOp = items[1]
        operand2: Callable[[Row], Value] = items[2]
        return lambda row: comp_op.eval(operand1(row), operand2(row))  # evaluate comparison

    def null_predicate(self, items: list) -> Predicate:
        operand: Callable[[Row], Value] = items[0]
        require_null: bool = items[2] is None
        return lambda row: boolean(operand(row) is None) if require_null else boolean(operand(row) is not None)

    def operand(self, items: List[Union[TableColumn, Value]]) -> Callable[[Row], Value]:
        return lambda row: row.search(items[0]) if isinstance(items[0], TableColumn) else items[0]

    ################################################################################################
    # 2.1 Create Table
    ################################################################################################

    def create_table_query(self, items: list):
        table_name, table_elements = items[2], items[3]
        if table_name in self.db.table_names():
            raise TableExistenceError

        # Classify table elements into cols, pk, fks.
        col_names, cols, pk, fks, ref_pks = set(), [], [], [], []
        for table_element in table_elements:
            tag: TableElementTag = table_element[0]
            if tag is TableElementTag.COL:
                col: Column = table_element[1]
                if col.name in col_names:
                    raise DuplicateColumnDefError

                col_names.add(col.name)
                cols.append(col)
            elif tag is TableElementTag.FK:
                fks.append(table_element[1])
                ref_pks.append(table_element[2])
            elif len(pk) == 0:  # if pk not declared yet
                pk = table_element[1]
            else:  # pk already declared
                raise DuplicatePrimaryKeyDefError

        # Create col_name_idx.
        col_name_idx = dict((col.name, i) for i, col in enumerate(cols))

        # Update KeyInfo in each column.
        for col_name in pk:
            if col_name not in col_name_idx:
                raise NonExistingColumnDefError(col_name)

            col = cols[col_name_idx[col_name]]
            col.add_pk()
            col.set_not_null()  # PK is not null by default
        for fk in fks:
            for col_name in fk.fk:
                if col_name not in col_name_idx:
                    raise NonExistingColumnDefError(col_name)

                col = cols[col_name_idx[col_name]]
                col.add_fk()

        self.__verify_create_table_query(table_name, col_name_idx, cols, pk, fks, ref_pks)

        # Ok, we are good.
        self.db.create_table(table_name, cols, pk, fks)

        Print.with_prompt(f"'{table_name}' table is created")

    def __verify_create_table_query(self, table_name: str, col_name_idx: Dict[str, int], cols: List[Column],
                                    pk: Key, fks: List[ForeignKey], ref_pks: List[Key]):
        # Check FK constraints
        for fk, ref_pk in zip(fks, ref_pks):
            if table_name == fk.ref_table:  # self referencing case
                ref_table_pk = pk
                ref_table_col_name_idx = col_name_idx
                ref_table_cols = cols
            else:
                ref_table_pk = self.db.pk(fk.ref_table)
                ref_table_col_name_idx = self.db.col_name_idx(fk.ref_table)
                ref_table_cols = self.db.cols(fk.ref_table)

                # Table existence check
                if ref_table_cols is None:
                    raise ReferenceTableExistenceError

            # FK match check - length
            if len(fk.fk) != len(ref_pk):
                raise ReferenceTypeError

            for fk_col_name, ref_pk_col_name in zip(fk.fk, ref_pk):
                # Column existence check
                if ref_pk_col_name not in ref_table_col_name_idx:
                    raise ReferenceColumnExistenceError

                # Column type check
                col = cols[col_name_idx[fk_col_name]]
                ref_table_col = ref_table_cols[ref_table_col_name_idx[ref_pk_col_name]]
                if col['type'] != ref_table_col['type']:
                    raise ReferenceTypeError

            # PK check
            if ref_pk != ref_table_pk:
                raise ReferenceNonPrimaryKeyError

    def table_element_list(self, items: List[tuple]) -> List[tuple]:
        return items[1:-1]  # remove parenthesis

    def table_element(self, items: List[tuple]) -> tuple:
        return items[0]  # PK, FK or COL with tag

    def column_definition(self, items: list) -> Tuple[TableElementTag, Column]:
        name = items[0]
        data_type = items[1]
        null = Column.Null('Y') if items[2] is None else Column.Null('N')
        return TableElementTag.COL, Column(name, null=null, **data_type)  # column metadata object

    def data_type(self, items: list) -> dict:
        """
        'TYPE_INT' | ('TYPE_CHAR', 'LP', 'INT', 'RP') | 'TYPE_DATE'.

        :return: {'data_type': type (, 'length': length)}
        """

        item = Column.Type(items[0].lower())
        ret = {'data_type': item}

        if item is Column.Type.CHAR:
            if items[2] <= 0:
                raise CharLengthError
            ret['length'] = items[2]

        return ret

    def table_constraint_definition(self, items: list) -> tuple:
        return items[0]  # PK or FK constraint with tag

    def primary_key_constraint(self, items: list) -> Tuple[TableElementTag, Key]:
        pk = items[2]
        return TableElementTag.PK, pk

    def referential_constraint(self, items: list) -> Tuple[TableElementTag, ForeignKey, Key]:
        fk = items[2]
        ref_table = items[4]
        ref_pk = items[5]
        return TableElementTag.FK, ForeignKey(fk, ref_table), ref_pk

    ################################################################################################
    # 2.2 Drop Table
    ################################################################################################

    def drop_table_query(self, items: List[str]):
        table_name = items[2]

        ref_cnt = self.db.ref_cnt(table_name)
        if ref_cnt is None:  # table existence check
            raise NoSuchTableError
        elif ref_cnt != 0:  # ref cnt check
            raise DropReferencedTableError(table_name)

        # Ok, we are good.
        self.db.drop_table(table_name)

        Print.with_prompt(f"'{table_name}' table is dropped")

    ################################################################################################
    # 2.3 Explain / Describe / Desc
    ################################################################################################

    @Print.Line()
    def explain_query(self, items: List[str]):
        table_name = items[1]

        cols = self.db.cols(table_name)
        if cols is None:  # table existence check
            raise NoSuchTableError

        # Ok, we are good.
        print('table_name', f'[{table_name}]')
        Print.with_padding('column_name', 'type', 'null', 'key')

        for col in cols:
            data_type = col.type.value
            if data_type is Column.Type.CHAR:
                data_type = f"char({col.length})"

            Print.with_padding(col.name, data_type, col.null.value, col.key.value)

    def describe_query(self, items: List[str]):
        self.explain_query(items)  # identical to explain

    def desc_query(self, items: List[str]):
        self.explain_query(items)  # identical to explain

    ################################################################################################
    # 2.4 Insert
    ################################################################################################

    def insert_query(self, items: list):
        table_name: str = items[2]
        target_col_names: List[str] = items[3]
        values = items[5]

        col_name_idx = self.db.col_name_idx(table_name)
        cols = self.db.cols(table_name)
        if cols is None:  # table existence check
            raise NoSuchTableError

        # Identify target columns and null columns.
        if target_col_names is None:
            null_col_names = set()
            target_col_names = [col.name for col in cols]
        else:
            null_col_names = set(col.name for col in cols)

            for col_name in target_col_names:
                if col_name not in null_col_names:
                    raise InsertColumnExistenceError(col_name)

                null_col_names.remove(col_name)

        # Create record to insert.
        record = self.__create_record(table_name, col_name_idx, cols, target_col_names, null_col_names, values)

        # Ok, we are good.
        self.db.insert_record(record)

        Print.with_prompt('The row is inserted')

    def __create_record(self, table_name: str, col_name_idx: Dict[str, int], cols: List[Column],
                        target_col_names: List[str], null_col_names: Set[str], values: List[Value]) -> Record:
        record = Record(table_name)

        # Verify number of values matches target columns.
        if len(target_col_names) != len(values):
            raise InsertTypeMismatchError

        # Verify value types and then add to the record.
        for col_name, value in zip(target_col_names, values):
            target_col = cols[col_name_idx[col_name]]

            if value is None:
                if target_col.null is Column.Null.NOT_NULL:
                    raise InsertColumnNonNullableError(col_name)
            elif target_col.type is Column.Type.INT:
                if not isinstance(value, int):
                    raise InsertTypeMismatchError
            elif target_col.type is Column.Type.DATE:
                if not isinstance(value, date):
                    raise InsertTypeMismatchError
            else:
                if not isinstance(value, str):
                    raise InsertTypeMismatchError

                # Truncate if string is longer that max size.
                length = target_col.length
                if len(value) > length:
                    value = value[:length]

            record[col_name] = value

        # Verify null columns are nullable and add to the record.
        for col_name in null_col_names:
            if cols[col_name_idx[col_name]].null is Column.Null.NOT_NULL:
                raise InsertColumnNonNullableError(col_name)

            record[col_name] = None

        return record

    ################################################################################################
    # 2.5 Delete
    ################################################################################################

    def delete_query(self, items: list):
        table_name: str = items[2]
        predicate: Predicate = items[3]
        if predicate is None:  # default where predicate is true
            predicate = trivial

        # Retrieve records from database.
        records = self.db.select_all_records(table_name)
        if records is None:  # table existence check
            raise NoSuchTableError

        # Where clause - filter records
        filtered_rows = filter(lambda record: predicate(Row.from_record(record[1])), records)
        idx_to_delete = [idx for idx, _ in filtered_rows]

        # Ok, we are good.
        self.db.delete_records(table_name, idx_to_delete)

        Print.with_prompt(f'{len(idx_to_delete)} row(s) are deleted')

    ################################################################################################
    # 2.6 Select
    ################################################################################################

    def select_query(self, items: list):
        selected_columns: List[TableColumn] = items[1]
        table_names: List[str] = items[3]
        predicate: Predicate = items[4]
        if predicate is None:  # default where predicate is true
            predicate = trivial

        # From clause - join tables
        rows = self.__join(table_names)

        # Where clause - filter rows
        rows = filter(predicate, rows)

        # Select clause - select columns
        num_cols = len(selected_columns)
        if num_cols == 0:  # wildcard
            selected_columns = self.__transform_wildcard(table_names)
            num_cols = len(selected_columns)

        rows_values = []
        for row in rows:
            row_values = []
            for table_column in selected_columns:
                try:
                    value = row.search(table_column)
                except (WhereTableNotSpecified, WhereColumnNotExist, WhereAmbiguousReference):
                    raise SelectColumnResolveError(table_column)

                row_values.append(value)

            rows_values.append(row_values)

        # Ok, we are good.
        Print.table_horizontal_line(num_cols)
        Print.with_padding(*selected_columns, sep='|')
        Print.table_horizontal_line(num_cols)

        for row_values in rows_values:
            for i in range(num_cols):
                if row_values[i] is None:  # null
                    row_values[i] = 'null'

            Print.with_padding(*row_values, sep='|')

        Print.table_horizontal_line(num_cols)

    def __join(self, table_names: List[str]) -> List[Row]:
        """Join the records from tables recursively."""

        if len(table_names) == 0:
            return [Row()]

        table_name = table_names[-1]

        records = self.db.select_all_records(table_name)
        if records is None:  # table existence check
            raise SelectTableExistenceError(table_name)

        rows = [Row.from_record(record[1]) for record in records]
        col_names = [col.name for col in self.db.cols(table_name)]

        ret = []
        left_rows = self.__join(table_names[:-1])  # recursive call
        for left_row in left_rows:
            for row in rows:
                ret.append(Row.merge(left_row, row))

        return ret

    def __transform_wildcard(self, table_names: List[str]) -> List[TableColumn]:
        """Retrieve a list of columns of joined table. It is guaranteed that the tables exist."""

        table_columns = [TableColumn(col.name, table_name) for table_name in table_names for col in
                         self.db.cols(table_name)]

        table_column_idx: Dict[str, Dict[str, int]] = dict()
        for i, table_column in enumerate(table_columns):
            if table_column.col_name not in table_column_idx:
                table_column_idx[table_column.col_name] = dict()

            table_column_idx[table_column.col_name][table_column.table_name] = i

        for col_name, idxs in table_column_idx.items():
            if len(idxs) == 1:
                idx = next(iter(idxs.values()))
                table_columns[idx].table_name = None

        return table_columns

    def select_list(self, items: List[TableColumn]) -> List[TableColumn]:
        return items  # list of TableColumn, empty iff wildcard

    ################################################################################################
    # 2.7 Show Tables
    ################################################################################################

    @Print.Line()
    def show_tables_query(self, items: List[Token]):
        for table_name in self.db.table_names():
            print(table_name)

    ################################################################################################
    # 2.9 Exit
    ################################################################################################

    def exit_cmd(self, items: List[Token]):
        exit(0)  # Exit with status code 0 (OK)
