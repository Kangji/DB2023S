from unittest import TestCase

from error import *


class TestSemanticsError(TestCase):
    def test_char_length(self):
        msg = str(CharLengthError())
        assert msg == 'Char length should be over 0'

    def test_no_such_table(self):
        msg = str(NoSuchTableError())
        assert msg == 'No such table'

    def test_where_incomparable(self):
        msg = str(WhereIncomparableError())
        assert msg == 'Where clause trying to compare incomparable values'

    def test_where_table_not_specified(self):
        msg = str(WhereTableNotSpecified())
        assert msg == 'Where clause trying to reference tables which are not specified'

    def test_where_column_not_exist(self):
        msg = str(WhereColumnNotExist())
        assert msg == 'Where clause trying to reference non existing column'

    def test_where_ambiguous_reference(self):
        msg = str(WhereAmbiguousReference())
        assert msg == 'Where clause contains ambiguous reference'

    def test_duplicate_column_def(self):
        msg = str(DuplicateColumnDefError())
        assert msg == 'Create table has failed: column definition is duplicated'

    def test_duplicate_primary_key_def(self):
        msg = str(DuplicatePrimaryKeyDefError())
        assert msg == 'Create table has failed: primary key definition is duplicated'

    def test_reference_type(self):
        msg = str(ReferenceTypeError())
        assert msg == 'Create table has failed: foreign key references wrong type'

    def test_reference_non_primary_key(self):
        msg = str(ReferenceNonPrimaryKeyError())
        assert msg == 'Create table has failed: foreign key references non primary key column'

    def test_reference_column_existence(self):
        msg = str(ReferenceColumnExistenceError())
        assert msg == 'Create table has failed: foreign key references non existing column'

    def test_reference_table_existence(self):
        msg = str(ReferenceTableExistenceError())
        assert msg == 'Create table has failed: foreign key references non existing table'

    def test_non_existing_column_def(self):
        msg = str(NonExistingColumnDefError('foo'))
        assert msg == "Create table has failed: 'foo' does not exist in column definition"

    def test_table_existence(self):
        msg = str(TableExistenceError())
        assert msg == 'Create table has failed: table with the same name already exists'

    def test_drop_referenced_table(self):
        msg = str(DropReferencedTableError('foo'))
        assert msg == "Drop table has failed: 'foo' is referenced by other table"

    def test_insert_type_mismatch(self):
        msg = str(InsertTypeMismatchError())
        assert msg == 'Insertion has failed: Types are not matched'

    def test_insert_column_existence(self):
        msg = str(InsertColumnExistenceError('foo'))
        assert msg == "Insertion has failed: 'foo' does not exist"

    def test_insert_column_non_nullable(self):
        msg = str(InsertColumnNonNullableError('foo'))
        assert msg == "Insertion has failed: 'foo' is not nullable"

    def test_select_table_existence(self):
        msg = str(SelectTableExistenceError('foo'))
        assert msg == "Selection has failed: 'foo' does not exist"

    def test_select_column_resolve(self):
        msg = str(SelectColumnResolveError('foo'))
        assert msg == "Selection has failed: fail to resolve 'foo'"
