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

class Result:
    class Mode:
        Human = 0
        Json = 1

    mode = Mode.Human

    messages = []

    def __init__(self, mode=Mode.Human):
        self.mode = mode

    def process_message(self, type, message, *args):
        message = message.format(*args)

        self.messages.append({
            "type": type,
            "message": message
        })

        if self.mode != Result.Mode.Human:
            # TODO: Implement Json output
            pass

        color = Fore.WHITE
        if type == "ok":
            color = Fore.GREEN
        if type == "warn":
            color = Fore.YELLOW
        if type == "err":
            color = Fore.RED

        print("{}[{}] {}{}".format(color, type.center(4).upper(), message, Style.RESET_ALL))

    def info(self, message, *args):
        self.process_message("info", message, *args)

    def ok(self, message, *args):
        self.process_message("ok", message, *args)

    def warn(self, message, *args):
        self.process_message("warn", message, *args)

    def error(self, message, *args):
        self.process_message("err", message, *args)
