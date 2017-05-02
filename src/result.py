# The MIT License (MIT)
#
# Copyright (c) 2017 Stefan Graupner
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

from colorama import Fore, Style
import json

class Result:
    silent = False

    class Mode:
        Human = 0
        Json = 1

    mode = Mode.Human

    def __init__(self, mode=Mode.Human, silent=False):
        self.mode = mode
        self.silent = silent

    def process_message(self, type, message, *args):
        if self.silent:
            return

        message = message.format(*args)

        if self.mode == Result.Mode.Human:
            self._print_human(type, message)

        if self.mode == Result.Mode.Json:
            self._print_json(type, message)

    def debug(self, message, *args):
        self.process_message("debug", message, *args)

    def info(self, message, *args):
        self.process_message("info", message, *args)

    def ok(self, message, *args):
        self.process_message("ok", message, *args)

    def warning(self, message, *args):
        self.process_message("warn", message, *args)

    def error(self, message, *args):
        self.process_message("err", message, *args)

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
