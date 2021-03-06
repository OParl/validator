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

class ValidatorException(Exception):
    """ A generic validator exception """

class ObjectValidationFailedException(Exception):
    """ A error occured during validation of an object """

class InvalidSeverityException(Exception):
    """ Raised when a severity for an extra check does not validate """

class ClientException(ValidatorException):
    """ A generic client exception """

class EndpointNotReachableException(ClientException):
    """ An endpoint was not reachable over the network """

class EndpointIsNotAnOParlEndpointException(ClientException):
    """ An endpoint is reachable but not valid oparl """
