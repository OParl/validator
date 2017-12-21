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

from oparl_validator.core.exceptions import InvalidSeverityException

class CheckResult:
    def __init__(self, severity : str, description : str):
        self.validate_severity(severity)

        self.severity = severity.lower()
        self.description = description
        self.context = context

    def validate_severity(self, severity : str):
        if type(severity) is not 'string':
            raise InvalidSeverityException()

        valid_severities = [
            'info',
            'warning',
            'error'
        ]

        if severity.lower() not in valid_severities:
            raise InvalidSeverityException()

    # Compatibility Methods for interop with OParl.ValidationResult
    def get_severity(self):
        return self.severity

    def get_description(self):
        return self.description

class Check:
    def evaluates_entity_type(self) -> [str]:
        """
            Return the type of entities which can be evaluated.

            Must return a list of entity type strings.
            Type strings must have the format `<typename>`,
            e.g. `file`. Types are always evaluated lowercased.
        """
        raise NotImplementedError

    def evaluate(self, entity : object) -> [CheckResult]:
        """
            Evaluate an entity.

            Must return a CheckResult list
        """
        raise NotImplementedError