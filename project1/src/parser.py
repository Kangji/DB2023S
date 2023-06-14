from lark import Lark


class SqlParserInjector:
    """
    The purpose of this class is a decorator.

    When the decorator is applied, it automatically injects the **Lark** object as an argument.

    Therefore, any decoratee must have **Lark** object as its last non-keyword argument.
    """

    DEFAULT_GRAMMAR = "grammar.lark"  # Default grammer file

    def __init__(self, file=DEFAULT_GRAMMAR):
        self.file = file

    def __call__(self, func):
        def wrapper(*args, **kwargs):
            parser = SqlParserInjector.create(self.file)
            return func(*args, parser, **kwargs)

        return wrapper

    @classmethod
    def create(cls, file=DEFAULT_GRAMMAR):
        """
        This classmethod is useful when you are not using decorator.

        :param file: relative path of grammar file.
        :return: Lark object
        """

        with open(file) as file:
            return Lark(file.read(), start="command", lexer="basic")
