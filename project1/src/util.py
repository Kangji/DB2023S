from json import JSONEncoder, JSONDecoder
from typing import Optional


class Padding:
    """Defines padding."""

    __slots__ = 'fill', 'align', 'width'

    def __init__(self, width: int, fill=' ', align='<'):
        self.width = width
        self.fill = fill
        self.align = align

    def apply_to(self, arg) -> str:
        """Apply padding."""

        return f'{arg:{self.fill}{self.align}{self.width}}'


class Print:
    """Print utility class."""

    # Enter my student ID.
    STUDENT_ID = "2017-18054"
    # Line.
    LINE = '--------------------------------------------------------------------------------'
    # Padding width.
    WIDTH = 20
    # Default padding.
    DEFAULT_PADING = Padding(WIDTH)

    class Line:
        """Print a line before and after function execution."""

        def __init__(self, file=None):
            self.file = file

        def __call__(self, func):
            def wrapper(*args, **kwargs):
                print(Print.LINE, file=self.file)
                ret = func(*args, **kwargs)
                print(Print.LINE, file=self.file)
                return ret

            return wrapper

    @classmethod
    def with_prompt(cls, *args, sep=' ', end='\n', file=None):
        """Print with prompt."""

        print("DB_" + cls.STUDENT_ID + ">", *args, sep=sep, end=end, file=file)

    @classmethod
    def with_padding(cls, *args, padding=DEFAULT_PADING, sep='', end='\n', file=None):
        """Print with padding."""

        args = tuple(padding.apply_to(arg) for arg in args)
        print('', *args, '', sep=sep, end=end, file=file)

    @classmethod
    def table_horizontal_line(cls, num_col: int, file=None):
        """Print a horizontal line for the table."""

        args = [''] * num_col
        padding = Padding(cls.WIDTH, fill='-')
        cls.with_padding(*args, padding=padding, sep='+', file=file)


class ExpectException:
    """A decorator for unit tests that expects an exception."""

    def __init__(self, expect):
        self.expect = expect

    def __call__(self, func):
        def wrapper(*args, **kwargs):
            try:
                func(*args, **kwargs)
                raise RuntimeError('An exception or error is expected')
            except self.expect:
                pass

        return wrapper


class Bytes:
    """Conversion utility class."""

    CHARSET = 'utf-8'
    encoder = JSONEncoder()
    decoder = JSONDecoder()

    @staticmethod
    def from_str(s: Optional[str]) -> Optional[bytes]:
        if s is not None:
            return bytes(s, Bytes.CHARSET)

    @staticmethod
    def from_int(n: Optional[int]) -> Optional[bytes]:
        if n is not None:
            return Bytes.from_str(str(n))

    @staticmethod
    def from_obj(obj) -> Optional[bytes]:
        if obj is not None:
            obj = Bytes.encoder.encode(obj)
            return Bytes.from_str(obj)

    @staticmethod
    def to_str(b: Optional[bytes]) -> Optional[str]:
        if b is not None:
            return str(b, Bytes.CHARSET)

    @staticmethod
    def to_int(b: Optional[bytes]) -> Optional[int]:
        if b is not None:
            return int(Bytes.to_str(b))

    @staticmethod
    def to_obj(b: Optional[bytes]):
        if b is not None:
            s = Bytes.to_str(b)
            return Bytes.decoder.decode(s)
