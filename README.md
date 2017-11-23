# OParl Validator

## Requirements

**on the system**

- liboparl and liboparl requirements
- redis (for caching)
- Python 3

**Python specific**

- pygobject
- requests
- colorama
- redis (only if you want to use caching)
- tqdm
- beautifultable (only for printing results to the console, use -oresult.json instead)

## Usage

```sh
./validate https://my.oparl.endpoint/
```

### Usage from other Python Code

You can also use the OParl Validator in your Python projects by simply
importing it and passing it url and desired options:

```python
from src.validator import Validator
result = Validator(url='https://my.oparl.endpoint/', options = { 'validate_schema': False, 'print_result': False })
```

**Mark this**: It is quite important to either redirect `stdout`/`stderr` or pass the `print_result`
option unless you explicitly want to have the validation progress and results passed to stdout.
You might also want to choose json formatting instead of plain text output.
