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

    def add_message(self, severity, text, context):
        

    def process_message(self, type, message, *args):
        if self.silent:
            return

        if type == Result.Verbosity.Default:
            type = Result.Verbosity.Error

        message = message.format(*args)

        if self.mode == Result.Mode.Human:
            self._print_human(type, message)

        if self.mode == Result.Mode.Json:
            self._print_json(type, message)

    def _print_human(self, type, message):
        color = Fore.WHITE
        if type == "ok":
            color = Fore.GREEN
        if type == "warn":
            color = Fore.YELLOW
        if type == "err":
            color = Fore.RED

        print("{}[{}] {}{}".format(color, type.center(4).upper(), message, Style.RESET_ALL))

    def _print_json(self, type, message):
        data = {
            "type": type,
            "message": message
        }

        print(json.dumps(data))
