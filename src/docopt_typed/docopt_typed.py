"""Thin wrapper around docopt-ng that converts parsed values to the annotated types"""

import json
import re
from collections.abc import Callable
from pathlib import Path
from typing import Any

from docopt import ParsedOptions, docopt

_EXAMPLE_DOC = """Usage:
  myprogram.py --speed=<int> INPUT_FILE [options]

Arguments:
  INPUT_FILE <path>       The path to read from

Options:
  -s, --speed=<int>       Speed in mph (integer)
  -v, --verbose=<bool>    Enable verbose logging (true/false) [default: false]
  -n, --name=<str>        Your name [default: Alice]
  -d, --debug             Enable debug mode (no value needed)

Examples:
  myprogram.py --speed=60 --verbose=true --name=Bob
"""


def _to_bool(value: object) -> bool:
    return value.lower() in ("true", "1", "yes", "on") if isinstance(value, str) else bool(value)


def _to_none(_value: object) -> None:
    return None


_TYPE_MAP: dict[str, Callable[[Any], Any]] = {
    "int": int,
    "float": float,
    "bool": _to_bool,
    "boolean": _to_bool,
    "str": str,
    "string": str,
    "text": str,
    "complex": complex,
    "json": json.loads,
    "dict": json.loads,
    "list": json.loads,
    "bytes": lambda s: str(s).encode(),  # UTF-8 by default behavior of .encode()
    "path": Path,
    "file": Path,
    "filepath": Path,
    "dir": Path,
    "directory": Path,
    "none": _to_none,
    "null": _to_none,  # alias for none
}


# The signature mirrors `docopt.docopt` so this stays a drop-in replacement, which is why
# `help` shadows a builtin and the booleans are positional.
def docopt_typed(
    doc: str,
    argv: list[str] | str | None = None,
    help: bool = True,  # noqa: A002, FBT001, FBT002
    version: Any = None,  # noqa: ANN401
    options_first: bool = False,  # noqa: FBT001, FBT002
) -> ParsedOptions:
    """Parse command-line arguments using docopt-ng and automatically convert types

    Supports: int, float, str, bool, None (as 'none' or 'null')
    """
    raw_args = docopt(doc, argv=argv, default_help=help, version=version, options_first=options_first)

    for key, value in raw_args.items():
        if value is None:
            continue

        # Try to infer type from docstring pattern (e.g., --speed=<int>)
        converter = _infer_type_from_spec(key, doc)

        if not converter:
            continue

        try:
            raw_args[key] = converter(value)
        except (ValueError, TypeError):
            # If conversion fails, keep as string (fallback)
            raw_args[key] = value

    return raw_args


def _infer_type_from_spec(arg_key: str, doc: str) -> Callable[[Any], Any] | None:
    """Extract the converter for the ``<type>`` syntax used in a docopt spec"""
    # Match patterns like --speed=<int> or <speed:int>
    # We look in the docstring for how arg_key was declared
    # But since raw_args has keys like '--speed', we scan original doc string
    #
    # For each possible pattern in the docstring, look for <key:type>
    # This is a simplified heuristic based on common docopt-ng usage
    for pattern in [
        rf"--{arg_key.lstrip('-')}=<(\w+)>",
        rf"<{arg_key.lstrip('-')}:(\w+)>",
        rf"--{arg_key.lstrip('-')}\s*=<(\w+)>",
        rf"{arg_key.lstrip('-')}\s* <(\w+)>",
    ]:
        match = re.search(pattern, doc)
        if match:
            type_name = match.group(1).lower()
            return _TYPE_MAP.get(type_name)
    return None


def _main() -> None:
    """Print the parsed types for the example usage above

    Running this module with ``--speed=60 --verbose=true --name=Bob input.txt`` reports
    speed as an int, verbose and debug as bools, name as a str, and INPUT_FILE as a Path.
    """
    args = docopt_typed(_EXAMPLE_DOC)
    print(args)

    print(f"Speed: {args.speed} ({type(args.speed)})")
    print(f"Verbose: {args.verbose} ({type(args.verbose)})")
    print(f"Name: {args.name} ({type(args.name)})")
    print(f"Debug: {args.debug} ({type(args.debug)})")
    print(f"INPUT_FILE: {args.INPUT_FILE} ({type(args.INPUT_FILE)})")


if __name__ == "__main__":
    _main()
