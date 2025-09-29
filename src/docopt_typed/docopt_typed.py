# docopt_wrapper.py

import json
import re
from pathlib import Path
from typing import Any, Callable

from docopt import ParsedOptions, docopt


def docopt_typed(
    doc: str,
    argv: list[str] | str | None = None,
    help: bool = True,
    version: Any = None,
    options_first: bool = False,
) -> ParsedOptions:
    """Parse command-line arguments using docopt-ng and automatically convert types

    Supports: int, float, str, bool, None (as 'none' or 'null')
    """
    # Parse raw arguments with docopt-ng
    raw_args = docopt(doc, argv=argv, default_help=help, version=version, options_first=options_first)

    # Convert each argument based on docstring inference

    for key, value in raw_args.items():
        if value is None:
            raw_args[key] = None
            continue

        # Try to infer type from docstring pattern (e.g., --speed=<int>)
        inferred_type = _infer_type_from_spec(key, doc)

        if not inferred_type:
            continue

        try:
            if isinstance(inferred_type, bool):
                raw_args[key] = value.lower() in ("true", "1", "yes", "on")
            elif inferred_type is type(None):  # none/null
                raw_args[key] = None
            else:
                raw_args[key] = inferred_type(value)
        except (ValueError, TypeError):
            # If conversion fails, keep as string (fallback)
            raw_args[key] = value

    return raw_args


def _infer_type_from_spec(arg_key: str, doc) -> type | None:
    """Extract type from <type> syntax in docopt spec"""
    type_map: dict[str, type] = {
        "int": int,
        "float": float,
        "bool": lambda x: x.lower() in ("true", "1", "yes", "on") if isinstance(x, str) else bool(x),
        "boolean": lambda x: x.lower() in ("true", "1", "yes", "on") if isinstance(x, str) else bool(x),
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
        "none": lambda x: None,
        "null": lambda x: None,  # alias for none
    }

    # Match patterns like --speed=<int> or <speed:int>
    # We look in the docstring for how arg_key was declared
    # But since raw_args has keys like '--speed', we scan original doc string

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
            return type_map.get(type_name)
    return None


if __name__ == "__main__":
    __doc__ = """Usage:
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

    args = docopt_typed(__doc__)
    print(args)

    print(f"Speed: {args.speed} ({type(args.speed)})")
    print(f"Verbose: {args.verbose} ({type(args.verbose)})")
    print(f"Name: {args.name} ({type(args.name)})")
    print(f"Debug: {args.debug} ({type(args.debug)})")
    print(f"INPUT_FILE: {args.INPUT_FILE} ({type(args.INPUT_FILE)})")

    # Example output if run with: --speed=60 --verbose=true --name=Bob
    # Speed: 60 (int)
    # Verbose: True (bool)
    # Name: Bob (str)
    # Debug: True (bool)
