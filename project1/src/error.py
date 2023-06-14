from abc import ABCMeta, abstractmethod

# noinspection PyUnresolvedReferences
from lark import UnexpectedInput as SqlSyntaxError


class SqlSemanticsError(Exception, metaclass=ABCMeta):
    """Top-level SQL semantics error."""

    def __str__(self):
        return self.msg()

    @staticmethod
    @abstractmethod
    def msg():
        pass


class CreateTableError(SqlSemanticsError, metaclass=ABCMeta):
    def __str__(self):
        return 'Create table has failed: ' + self.msg()


class DropTableError(SqlSemanticsError, metaclass=ABCMeta):
    def __str__(self):
        return 'Drop table has failed: ' + self.msg()


class InsertError(SqlSemanticsError, metaclass=ABCMeta):
    def __str__(self):
        return 'Insertion has failed: ' + self.msg()


class SelectError(SqlSemanticsError, metaclass=ABCMeta):
    def __str__(self):
        return 'Selection has failed: ' + self.msg()


class CharLengthError(SqlSemanticsError):
    @staticmethod
    def msg():
        return 'Char length should be over 0'


class NoSuchTableError(SqlSemanticsError):
    @staticmethod
    def msg():
        return 'No such table'


class WhereIncomparableError(SqlSemanticsError):
    @staticmethod
    def msg():
        return 'Where clause trying to compare incomparable values'


class WhereTableNotSpecified(SqlSemanticsError):
    @staticmethod
    def msg():
        return 'Where clause trying to reference tables which are not specified'


class WhereColumnNotExist(SqlSemanticsError):
    @staticmethod
    def msg():
        return 'Where clause trying to reference non existing column'


class WhereAmbiguousReference(SqlSemanticsError):
    @staticmethod
    def msg():
        return 'Where clause contains ambiguous reference'


class DuplicateColumnDefError(CreateTableError):
    @staticmethod
    def msg():
        return 'column definition is duplicated'


class DuplicatePrimaryKeyDefError(CreateTableError):
    @staticmethod
    def msg():
        return 'primary key definition is duplicated'


class ReferenceTypeError(CreateTableError):
    @staticmethod
    def msg():
        return 'foreign key references wrong type'


class ReferenceNonPrimaryKeyError(CreateTableError):
    @staticmethod
    def msg():
        return 'foreign key references non primary key column'


class ReferenceColumnExistenceError(CreateTableError):
    @staticmethod
    def msg():
        return 'foreign key references non existing column'


class ReferenceTableExistenceError(CreateTableError):
    @staticmethod
    def msg():
        return 'foreign key references non existing table'


class NonExistingColumnDefError(CreateTableError):
    def __init__(self, col_name):
        self.col_name = col_name

    def msg(self):
        return f"'{self.col_name}' does not exist in column definition"


class TableExistenceError(CreateTableError):
    @staticmethod
    def msg():
        return 'table with the same name already exists'


class DropReferencedTableError(DropTableError):
    def __init__(self, table_name):
        self.table_name = table_name

    def msg(self):
        return f"'{self.table_name}' is referenced by other table"


class InsertTypeMismatchError(InsertError):
    @staticmethod
    def msg():
        return 'Types are not matched'


class InsertColumnExistenceError(InsertError):
    def __init__(self, col_name):
        self.col_name = col_name

    def msg(self):
        return f"'{self.col_name}' does not exist"


class InsertColumnNonNullableError(InsertError):
    def __init__(self, col_name):
        self.col_name = col_name

    def msg(self):
        return f"'{self.col_name}' is not nullable"


class SelectTableExistenceError(SelectError):
    def __init__(self, table_name):
        self.table_name = table_name

    def msg(self):
        return f"'{self.table_name}' does not exist"


class SelectColumnResolveError(SelectError):
    def __init__(self, col_name):
        self.col_name = col_name

    def msg(self):
        return f"fail to resolve '{self.col_name}'"
