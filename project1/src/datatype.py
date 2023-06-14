import datetime
from enum import Enum
from typing import List, Union, Callable, Dict

from error import SqlSyntaxError, WhereIncomparableError, WhereColumnNotExist, WhereAmbiguousReference, \
    WhereTableNotSpecified


####################################################################################################
# Value
####################################################################################################

class date(dict):
    """Date. It is an immutable object."""

    __slots__ = 'year', 'month', 'day'

    def __init__(self, year: int, month: int, day: int):
        super().__init__()
        self['year'] = self.year = year
        self['month'] = self.month = month
        self['day'] = self.day = day

    def __str__(self):
        return f'{self.year:0>4}-{self.month:0>2}-{self.day:0>2}'

    def __format__(self, format_spec):
        return str(self).__format__(format_spec)

    def __lt__(self, other) -> bool:
        if self.year < other.year:
            return True
        elif self.year > other.year:
            return False

        if self.month < other.month:
            return True
        elif self.month > other.month:
            return False

        return self.day < other.day

    def __le__(self, other) -> bool:
        return self.__eq__(other) or self.__lt__(other)

    def __gt__(self, other) -> bool:
        return not self.__le__(other)

    def __ge__(self, other) -> bool:
        return not self.__lt__(other)

    def __eq__(self, other) -> bool:
        return self.year == other.year and self.month == other.month and self.day == other.day

    def __ne__(self, other) -> bool:
        return not self.__eq__(other)

    @classmethod
    def from_dict(cls, inner: Dict[str, int]):
        return cls(inner['year'], inner['month'], inner['day'])

    @classmethod
    def fromisoformat(cls, date_string: str):
        try:
            datetime_date = datetime.date.fromisoformat(date_string)
        except ValueError:
            raise SqlSyntaxError
        return cls(datetime_date.year, datetime_date.month, datetime_date.day)


class boolean(Enum):
    """Three valued logic. (true, unknown, and false)"""

    true = True
    false = False
    unknown = None

    def __bool__(self):
        return self is boolean.true

    def __and__(self, other):
        if not isinstance(other, boolean):
            raise TypeError(f"unsupported operand type(s) for &: '{type(self).__name__}' and '{type(other).__name__}'")

        if self is boolean.true:
            return other
        elif self is boolean.false or other is boolean.false:
            return boolean.false
        else:
            return boolean.unknown

    def __or__(self, other):
        if not isinstance(other, boolean):
            raise TypeError(f"unsupported operand type(s) for |: '{type(self).__name__}' and '{type(other).__name__}'")

        if self is boolean.false:
            return other
        elif self is boolean.true or other is boolean.true:
            return boolean.true
        else:
            return boolean.unknown

    def __neg__(self):
        if self is boolean.true:
            return boolean.false
        elif self is boolean.false:
            return boolean.true
        else:
            return boolean.unknown


Value = Union[int, str, date, None]


class CompOp(Enum):
    """Comparison operators."""

    LT = '<'
    GT = '>'
    LE = '<='
    GE = '>='
    EQ = '='
    NE = '!='

    def eval(self, operand1: Value, operand2: Value) -> boolean:
        if operand1 is None or operand2 is None:
            return boolean.unknown
        elif type(operand1) is not type(operand2):
            raise WhereIncomparableError

        if self is self.LT:
            return boolean(operand1 < operand2)
        elif self is self.GT:
            return boolean(operand1 > operand2)
        elif self is self.LE:
            return boolean(operand1 <= operand2)
        elif self is self.GE:
            return boolean(operand1 >= operand2)
        elif self is self.EQ:
            return boolean(operand1 == operand2)
        elif self is self.NE:
            return boolean(operand1 != operand2)


####################################################################################################
# Metadata
####################################################################################################

Key = List[str]


class ForeignKey(dict):
    """Foreign key definition."""

    __slots__ = 'fk', 'ref_table'

    def __init__(self, fk: Key, ref_table: str):
        super().__init__()
        self['fk'] = self.fk = fk
        self['ref_table'] = self.ref_table = ref_table

    @classmethod
    def from_dict(cls, inner: Dict[str, Union[Key, str]]):
        return cls(inner['fk'], inner['ref_table'])


class Column(dict):
    """Column definition."""

    class Type(Enum):
        INT = 'int'
        DATE = 'date'
        CHAR = 'char'

    class Null(Enum):
        NULL = 'Y'
        NOT_NULL = 'N'

    class KeyInfo(Enum):
        NONE = ''
        PK = 'PRI'
        FK = 'FOR'
        BOTH = 'PRI/FOR'

    __slots__ = 'name', 'type', 'length', 'null', 'key'

    def __init__(self, name: str, data_type: Type, length: int = None, null=Null.NULL, key=KeyInfo.NONE):
        super().__init__()

        self['name'] = name
        self.name = name

        if data_type is self.Type.CHAR:
            self['type'] = {'length': length}
            self.length = length
        else:
            self['type'] = data_type.value
            self.length = None
        self.type = data_type

        self['null'] = null.value
        self.null = null

        self['key'] = key.value
        self.key = key

    @classmethod
    def from_dict(cls, inner: Dict[str, Union[str, Dict[str, int]]]):
        if isinstance(inner['type'], dict):
            data_type = cls.Type.CHAR
            length = inner['type']['length']
        else:
            data_type = cls.Type(inner['type'])
            length = None

        return cls(inner['name'], data_type, length, cls.Null(inner['null']), cls.KeyInfo(inner['key']))

    def add_pk(self):
        """Add primary key constraint."""

        if self.key is self.KeyInfo.NONE or self.key is self.KeyInfo.PK:
            self['key'] = self.KeyInfo.PK.value
            self.key = self.KeyInfo.PK
        else:
            self['key'] = self.KeyInfo.BOTH.value
            self.key = self.KeyInfo.BOTH

    def add_fk(self):
        """Add referential constraint."""

        if self.key is self.KeyInfo.NONE or self.key is self.KeyInfo.FK:
            self['key'] = self.KeyInfo.FK.value
            self.key = self.KeyInfo.FK
        else:
            self['key'] = self.KeyInfo.BOTH.value
            self.key = self.KeyInfo.BOTH

    def set_not_null(self):
        """Set to not null."""

        self['null'] = self.Null.NOT_NULL.value
        self.null = self.Null.NOT_NULL


####################################################################################################
# Identifier
####################################################################################################

class TableColumn:
    """A column name with optional table name."""

    __slots__ = 'table_name', 'col_name'

    def __init__(self, col_name: str, table_name: str = None):
        self.table_name = table_name
        self.col_name = col_name

    def __str__(self):
        if self.table_name is not None:
            return f'{self.table_name}.{self.col_name}'
        else:
            return self.col_name

    def __format__(self, format_spec):
        return str(self).__format__(format_spec)


####################################################################################################
# Data
####################################################################################################

class Record(dict):
    """Record. It's structure is: {'col1': value, ...}."""

    __slots__ = 'table_name'

    def __init__(self, table_name: str):
        super().__init__()
        self.table_name = table_name

    @classmethod
    def from_dict(cls, table_name: str, inner: Dict[str, Value]):
        ret = cls(table_name)
        for col_name in inner:
            ret[col_name] = inner[col_name]

        return ret


class Row(dict):
    """Row. It's structure is: {'col1': {'table1' : value, ...}, ...}."""

    __slots__ = 'table_names'

    def __init__(self):
        super().__init__()
        self.table_names = set()

    @classmethod
    def from_dict(cls, inner: Dict[str, Dict[str, Value]]):
        ret = Row()
        for col_name in inner:
            for table_name in inner[col_name]:
                ret.add_value(col_name, table_name, inner[col_name][table_name])

        return ret

    @classmethod
    def from_record(cls, record: Record):
        ret = Row()
        for col_name in record:
            ret.add_value(col_name, record.table_name, record[col_name])

        return ret

    @classmethod
    def merge(cls, left, right):
        """Join two rows. It creates the new object."""

        ret = Row.from_dict(left)
        for col_name in right:
            for table_name in right[col_name]:
                ret.add_value(col_name, table_name, right[col_name][table_name])

        return ret

    def add_value(self, col_name: str, table_name: str, value: Value):
        if table_name not in self.table_names:
            self.table_names.add(table_name)

        if col_name not in self:
            self[col_name] = dict()

        self[col_name][table_name] = value

    def search(self, table_column: TableColumn) -> Value:
        """
        Search for the column value.

        :param table_column: table name and column name of value to search
        :return: Value
        :raise WhereTableNotSpecified: table not specified
        :raise WhereColumnNotExist: cannot find column
        :raise WhereAmbiguousReference: more than one available target column
        """

        if table_column.table_name is not None and table_column.table_name not in self.table_names:
            raise WhereTableNotSpecified

        try:
            values: Dict[str, Value] = self[table_column.col_name]

            if table_column.table_name is not None:
                return values[table_column.table_name]
            elif len(values) != 1:
                raise WhereAmbiguousReference
            else:
                return next(iter(values.values()))
        except KeyError:
            raise WhereColumnNotExist


Predicate = Callable[[Row], boolean]
