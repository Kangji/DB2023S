from lark.exceptions import VisitError

from app import App
from db import DbApi
from error import SqlSyntaxError, SqlSemanticsError
from parser import SqlParserInjector
from util import Print


def read_queries():
    """
    Read queries from stdin.

    A single line of input consists of one or more queries, each of them are terminated by ';'.

    However, the last query might not have been terminated yet, if it is not terminated by ';'.
    In this case, the query must be continued by next line of input.

    :return: A list of queries.
    """

    unterminated_query = ''
    terminated_queries = []

    Print.with_prompt(end=' ')
    while True:
        new_queries = (unterminated_query + input() + '\n').split(';')
        terminated_queries.extend(new_queries[:-1])
        unterminated_query = new_queries[-1]

        # If the unterminated query is empty or whitespaces, it is not a query, and input terminates.
        if len(unterminated_query.strip()) == 0:
            break

    return terminated_queries


if __name__ == "__main__":
    db = DbApi('myDB.db')
    app = App(db)
    parser = SqlParserInjector.create()

    while True:
        try:
            for query in read_queries():
                tree = parser.parse(query)
                app.transform(tree)
        except SqlSyntaxError:
            Print.with_prompt('Syntax error')
        except VisitError as e:
            # Since every exception raised by Transformer is wrapped with 'VisitError'
            # so here we unwrap it.
            try:
                raise e.orig_exc
            except SqlSemanticsError as e:
                Print.with_prompt(e)
