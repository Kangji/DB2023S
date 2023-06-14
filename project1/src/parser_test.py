from unittest import TestCase

from lark.exceptions import UnexpectedInput

from parser import SqlParserInjector
from util import ExpectException


# noinspection SqlDialectInspection
class TestSqlParser(TestCase):
    @SqlParserInjector()
    def test_create_table(self, parser):
        sql = """
        create table student(
            id int not null,
            name char(10),
            register date,
            dept_id int,
            PRIMARY key (id),
            FOREIGN kEy (dept_id) references dept (id) 
        )
        """
        parser.parse(sql)

    @SqlParserInjector()
    @ExpectException(UnexpectedInput)
    def test_create_table_fail(self, parser):
        sql = "create table student()"
        parser.parse(sql)

    @SqlParserInjector()
    def test_drop_table(self, parser):
        sql = " drop table student     "
        parser.parse(sql)

    @SqlParserInjector()
    def test_explain(self, parser):
        sql = "explain student"
        parser.parse(sql)

    @SqlParserInjector()
    def test_describe(self, parser):
        sql = "describe student"
        parser.parse(sql)

    @SqlParserInjector()
    def test_desc(self, parser):
        sql = "desc student"
        parser.parse(sql)

    @SqlParserInjector()
    def test_insert(self, parser):
        sql = """
        insert into student (id, name, dept_id)
            values (1, 'John', 3)
        """
        parser.parse(sql)

        sql = """
        insert into student
            values (1, 'John', 3)
        """
        parser.parse(sql)

    @SqlParserInjector()
    @ExpectException(UnexpectedInput)
    def test_insert_fail(self, parser):
        sql = """
        insert into student
            values 3
        """
        parser.parse(sql)

    @SqlParserInjector()
    def test_delete(self, parser):
        sql = "delete from student where id = 1"
        parser.parse(sql)

    @SqlParserInjector()
    @ExpectException(UnexpectedInput)
    def test_delete_fail(self, parser):
        sql = "delete from student where id"
        parser.parse(sql)

    @SqlParserInjector()
    def test_select(self, parser):
        sql = "select ID from student"
        parser.parse(sql)

    @SqlParserInjector()
    def test_show_tables(self, parser):
        sql = "show tables"
        parser.parse(sql)

    @SqlParserInjector()
    def test_update(self, parser):
        sql = "update student set dept_id = 5 where name = 'John'"
        parser.parse(sql)

    @SqlParserInjector()
    @ExpectException(UnexpectedInput)
    def test_update_fail(self, parser):
        sql = "update student where name = 'John'"
        parser.parse(sql)

    @SqlParserInjector()
    def test_exit(self, parser):
        sql = "exit"
        parser.parse(sql)

    @SqlParserInjector()
    @ExpectException(UnexpectedInput)
    def test_syntax_error(self, parser):
        sql = "asdf"
        parser.parse(sql)
