"""
Provides capability to print in color to the terminal in both Windows and Linux.
"""

import sys

class LinuxColorPrinter(object):
    """
    Print in color on linux
    """

    BLUE = 'b'
    GREEN = 'g'
    RED = 'r'
    INTENSITY = 'i'
    WHITE = RED + GREEN + BLUE

    def __init__(self):
        pass

    def write(self, text, output_file=None, fg=None, bg=None):
        """
        Print the text in color to the output_file
        uses stdout if output_file is None
        """
        if output_file is None:
            output_file = sys.stdout

        text = self._ansi_wrap(text, fg, bg)
        output_file.write(text)

    @staticmethod
    def _to_code(rgb):
        """
        Translate strings containing 'rgb' characters to numerical color codes
        """
        code = 0
        if 'r' in rgb:
            code += 1

        if 'g' in rgb:
            code += 2

        if 'b' in rgb:
            code += 4
        return code

    def _ansi_wrap(self, text, fg, bg):
        """
        Wrap the text into ANSI color escape codes
        fg -- the foreground color
        bg -- the background color
        """
        codes = []

        if fg is not None:
            codes.append(30 + self._to_code(fg))

        if bg is not None:
            codes.append(40 + self._to_code(bg))

        if fg is not None and 'i' in fg:
            codes.append(1)  # Bold

        if bg is not None and 'i' in bg:
            codes.append(4)  # Underscore

        return "\033[" + ";".join([str(code) for code in codes]) + "m" + text + "\033[0m"


class NoColorPrinter(object):
    """
    Dummy printer that does not print in color
    """
    def __init__(self):
        pass

    @staticmethod
    def write(text, output_file=None, fg=None, bg=None):  # pylint: disable=unused-argument
        """
        Print the text in color to the output_file
        uses stdout if output_file is None
        """
        if output_file is None:
            output_file = sys.stdout
        output_file.write(text)


NO_COLOR_PRINTER = NoColorPrinter()
COLOR_PRINTER = LinuxColorPrinter()
