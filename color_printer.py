#******************************************************************************
# * Copyright (c) 2019, XtremeDV. All rights reserved.
# *
# * Licensed under the Apache License, Version 2.0 (the "License");
# * you may not use this file except in compliance with the License.
# * You may obtain a copy of the License at
# *
# * http://www.apache.org/licenses/LICENSE-2.0
# *
# * Unless required by applicable law or agreed to in writing, software
# * distributed under the License is distributed on an "AS IS" BASIS,
# * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# * See the License for the specific language governing permissions and
# * limitations under the License.
# *
# * Author: Jude Zhang, Email: zhajio.1988@gmail.com
# *******************************************************************************
# Copyright (c) 2014-2018, Lars Asplund lars.anders.asplund@gmail.com
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
