"""
The MIT License (MIT)

Copyright (c) 2017 Stefan Graupner

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

import json
from colorama import Fore, Style


class Result(object):
    """ Validator result object """
    class Mode(object):
        """ Output mode """
        Human = 0
        Json = 1

    class Verbosity(object):
        """
            Result.Verbosity simultaneously describes the verbosity of the output
        """
        Default = 0
        Info = 1
        Warning = 2
        Error = 3
        Debug = 4

    class Severity(object):
        """
            Severity of messages - This is quite similar to the output verbosity except
            that there is no default.
        """
        Debug = 0
        Info = 1
        Warning = 2
        Error = 3

    silent = False

    mode = Mode.Human
    verbosity = Verbosity.Default

    def __init__(self, mode=Mode.Human, silent=False, verbosity=Verbosity.Default):
        self.mode = mode
        self.silent = silent
        self.verbosity = verbosity

    def add_message(self, severity, text, *context):
        if self.silent:
            return

        if context and len(context) > 0:
            text = text.format(context)

        if self.mode == Result.Mode.Json:
            data = {
                "severity": self.format_severity(severity),
                "text": text,
                "context": context
            }

            print(json.dumps(data))

        if self.mode == Result.Mode.Human:
            color = Fore.WHITE
            if severity == Result.Severity.Info:
                color = Fore.GREEN
            if severity == Result.Severity.Warning:
                color = Fore.YELLOW
            if severity == Result.Severity.Error:
                color = Fore.RED

            print("{}[{}] {}{}".format(color, self.format_severity(severity).center(8).upper(), text, Style.RESET_ALL))

    def format_severity(self, severity):
        if severity == Result.Severity.Debug:
            return "Debug"
        if severity == Result.Severity.Info:
            return "Info"
        if severity == Result.Severity.Warning:
            return "Warning"
        if severity == Result.Severity.Error:
            return "Error"

    def debug(self, text, *context):
        self.add_message(Result.Severity.Debug, text, context)
    
    def info(self, text, *context):
        self.add_message(Result.Severity.Info, text, context)

    def warning(self, text, *context):
        self.add_message(Result.Severity.Warning, text, context)

    def error(self, text, *context):
        self.add_message(Result.Severity.Error, text, context)