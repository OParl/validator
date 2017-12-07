# OParl Validator

Checks an oparl server for compliance with the [oparl specification](https://github.com/oparl/spec)

## Quickstart with docker

We do not yet offer prebuilt images, so you need to build the container locally:

```bash
docker build . -t oparl-validator
```
Run the validator with

```bash
docker run --name oparl-validator oparl-validator [entrypoint]
```

## Requirements

**on the system**

- liboparl and liboparl requirements
- redis
- Python >= 3.5

**Python specific**

- pygobject
- requests
- redis
- tqdm
- beautifultable

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

### General remarks on embedding the Validator

The OParl Validator supports a `--porcelain` output mode which will output all messages and progress reports
in the [Json Patch](http://jsonpatch.com/) Format. However, in porcelain mode the output will never include
the validation result. Instead, you must set an explicit output file.

**All output the validator produces while running is sent to `stdout`.**

## Development Setup

This repository uses git hooks which are being tracked in the repository under the `.hooks` directory.
To configure these hooks on your clone, please run

`git config include.path ../.gitconfig`

in the repository root directory after cloning.
