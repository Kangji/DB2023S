from typing import Tuple


class Print:
    """Print utility class."""

    @classmethod
    def table(cls, header: Tuple[str, ...], aligns: Tuple[str, ...], records: Tuple[Tuple, ...]):
        """Print a table."""

        widths = tuple(len(item) for item in header)
        for record in records:
            widths = tuple(max(width, len(str(value))) for width, value in zip(widths, record))

        cls.horizontal_line(widths)
        cls.header(header, widths)
        cls.horizontal_line(widths)
        for record in records:
            cls.record(record, aligns, widths)
        if len(records) > 0:
            cls.horizontal_line(widths)

    @classmethod
    def header(cls, header: Tuple[str, ...], widths: Tuple[int, ...]):
        """Print a header line."""

        args = list(f' {arg:<{width}} ' for arg, width in zip(header, widths))
        print('', *args, '', sep='|')

    @classmethod
    def record(cls, record: Tuple, aligns: Tuple[str, ...], widths: Tuple[int, ...]):
        """Print a record."""

        args = list(f' {str(value):{align}{width}} ' for value, align, width in zip(record, aligns, widths))
        print('', *args, '', sep='|')

    @classmethod
    def horizontal_line(cls, widths: Tuple[int, ...]):
        """Print a horizontal line for the table."""

        args = list('-' * (width + 2) for width in widths)
        print('', *args, '', sep='+')
