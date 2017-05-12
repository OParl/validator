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
    """ 
        Validation Result 

        The validation result contains a set of messages for each object
        type as well as some general statistics and messages regarding
        validation events that do not belong into the above categories.
        That last category, among other things, keeps taps on what objects
        or files were unreachable.
    """

    class Mode(object):
        """ Output mode """
        Human = 0
        Json = 1

    class Verbosity(object):
        """
            Result.Verbosity simultaneously describes the verbosity of the output
        """
        Debug = 0
        Info = 1
        Warning = 2
        Error = 3

    class Severity(Verbosity):
        """
            Type redifinition of Verbosity for Severity
        """
        pass

    silent = False

    mode = Mode.Human
    verbosity = Verbosity.Error

    total_entities = 0
    valid_entities = 0
    failed_entities = 0

    object_messages = {}

    def __init__(self, mode, silent, verbosity):
        self.mode = mode
        self.silent = silent
        self.verbosity = verbosity

    def check_severity(self, severity):
        if severity >= self.verbosity:
            return False
        
        return True

    def format_severity(self, severity):
        if severity == Result.Severity.Debug:
            return "Debug"
        if severity == Result.Severity.Info:
            return "Info"
        if severity == Result.Severity.Warning:
            return "Warning"
        if severity == Result.Severity.Error:
            return "Error"