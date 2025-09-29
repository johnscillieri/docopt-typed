# docopt-typed

docopt-typed is a lightweight helper around [docopt-ng](https://pypi.org/project/docopt-ng/) that keeps the ergonomics of docstrings-as-interfaces while adding automatic type conversion. Annotate your usage text with the familiar `<type>` markers and receive a `ParsedOptions` object whose values already match those types.

## Features

- Works as a drop-in replacement for `docopt` while returning the same `ParsedOptions` object
- Converts values to Python types by reading `<type>` (or `<name:type>`) hints in the usage text
- Supports common primitives (`int`, `float`, `bool`, `str`, `path`) plus JSON-backed structures, complex numbers, and `none/null`
- Keeps raw strings when a conversion fails so you can decide how to handle edge cases
- Treats option and positional argument annotations the same, so flags and required arguments can both be typed

## Installation

```bash
pip install docopt-typed
```

or

```bash
uv add docopt-typed
```

## Usage

Import `docopt_typed` instead of `docopt` and describe your CLI exactly as you would with docopt-ng, adding type annotations inside angle brackets. The example below mirrors the runnable block at the bottom of `src/docopt_typed/docopt_typed.py` and shows both option and positional annotations:

```python
from docopt_typed import docopt_typed

__doc__ = """Usage:
  myprogram.py --speed=<int> INPUT_FILE [options]

Arguments:
  INPUT_FILE <path>       The path to read from

Options:
  -s, --speed=<int>       Speed in mph (integer)
  -v, --verbose=<bool>    Enable verbose logging (true/false) [default: false]
  -n, --name=<str>        Your name [default: Alice]
  -d, --debug             Enable debug mode (no value needed)
"""

args = docopt_typed(__doc__)
print(args.speed, type(args.speed))        # 60 <class 'int'>
print(args.verbose, type(args.verbose))    # True <class 'bool'>
print(args.name, type(args.name))          # Bob <class 'str'>
print(args.debug, type(args.debug))        # True <class 'bool'>
print(args.INPUT_FILE, type(args.INPUT_FILE))  # Positional argument converted to Path
```

Running the script as `python myprogram.py --speed=60 --verbose=true --name=Bob input.txt` produces an already-typed result. Positional arguments are annotated by placing the type marker alongside the name (e.g. `INPUT_FILE <path>` in the `Arguments` section), while options continue to use the `--flag=<type>` pattern.

## Supported type hints

The converter looks for the `<type>` token associated with each option or argument name and applies the matching callable:
- `int`, `float`, `complex`
- `bool`, `boolean` (accepts `true/false`, `1/0`, `yes/no`, `on/off` in any case)
- `str`, `string`, `text`
- `json`, `dict`, `list` (parsed with `json.loads`)
- `bytes` (UTF-8 encoding of the provided value)
- `path`, `file`, `filepath`, `dir`, `directory` (converted to `pathlib.Path`)
- `none`, `null` (converted to `None`)

Any pattern that cannot be converted cleanly is left untouched as the original string so you can handle validation yourself.

## Attribute access and testing

`docopt_typed` returns the same `ParsedOptions` object as docopt-ng, so you can access results via `args["--speed"]` or `args.speed`. The accompanying tests in `tests/test_docopt.py` demonstrate how to supply custom argument lists, assert on types, and verify behavior for short-form flags and various boolean spellings.

## Error handling

When a hint is missing, misspelled, or unsupported, the original string is preserved. This mirrors docopt's philosophy of trusting the usage documentation and keeps the wrapper safe as a drop-in replacement.
