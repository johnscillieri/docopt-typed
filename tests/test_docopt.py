"""
Test cases for docopt-typed wrapper
"""

import sys
from io import StringIO
from contextlib import redirect_stdout, redirect_stderr

from docopt_typed import docopt_typed


def test_basic_parsing():
    """Test basic argument parsing with type conversion"""

    doc = """
    Test program

    Usage:
        test.py --speed=<int> --count=<float> --verbose=<bool>

    Options:
        --speed=<int>     Speed value (integer)
        --count=<float>   Count value (float)
        --verbose=<bool>  Verbose output (boolean)
    """

    # Test with integer, float, and boolean values
    test_args = ["--speed", "50", "--count", "3.2", "--verbose", "true"]
    args = docopt_typed(doc, test_args)

    print("=== Basic Parsing Test ===")
    print(f"Speed: {args.speed} (type: {type(args.speed)})")
    print(f"Count: {args.count} (type: {type(args.count)})")
    print(f"Verbose: {args.verbose} (type: {type(args.verbose)})")

    # Verify types
    assert isinstance(args.speed, int), f"Expected int, got {type(args.speed)}"
    assert isinstance(args.count, float), f"Expected float, got {type(args.count)}"
    assert isinstance(args.verbose, bool), f"Expected bool, got {type(args.verbose)}"

    # Verify values
    assert args.speed == 50, f"Expected speed=50, got {args.speed}"
    assert args.count == 3.2, f"Expected count=3.2, got {args.count}"
    assert args.verbose == True, f"Expected verbose=True, got {args.verbose}"

    print("✓ Basic parsing test passed\n")


def test_short_forms():
    """Test with short forms of arguments"""

    doc = """
    Test program with short forms

    Usage:
        test.py -s <int> -c <float> -v <bool>

    Options:
        -s <int>     Speed value (integer)
        -c <float>   Count value (float)
        -v <bool>    Verbose output (boolean)
    """

    test_args = ["-s", "100", "-c", "5.7", "-v", "false"]
    args = docopt_typed(doc, test_args)

    print("=== Short Forms Test ===")
    print(f"Speed: {args.s} (type: {type(args.s)})")
    print(f"Count: {args.c} (type: {type(args.c)})")
    print(f"Verbose: {args.v} (type: {type(args.v)})")

    # Verify types
    assert isinstance(args.s, int), f"Expected int, got {type(args.s)}"
    assert isinstance(args.c, float), f"Expected float, got {type(args.c)}"
    assert isinstance(args.v, bool), f"Expected bool, got {type(args.v)}"

    # Verify values
    assert args.s == 100, f"Expected speed=100, got {args.s}"
    assert args.c == 5.7, f"Expected count=5.7, got {args.c}"
    assert args.v == False, f"Expected verbose=False, got {args.v}"

    print("✓ Short forms test passed\n")


def test_string_and_other_types():
    """Test with string conversion and other types"""

    doc = """
    Test program with various types

    Usage:
        test.py --name=<str> --age=<int> --price=<float>

    Options:
        --name=<str>    Name value (string)
        --age=<int>     Age value (integer)
        --price=<float> Price value (float)
    """

    test_args = ["--name", "John Doe", "--age", "25", "--price", "99.99"]
    args = docopt_typed(doc, test_args)

    print("=== String and Other Types Test ===")
    print(f"Name: {args.name} (type: {type(args.name)})")
    print(f"Age: {args.age} (type: {type(args.age)})")
    print(f"Price: {args.price} (type: {type(args.price)})")

    # Verify types
    assert isinstance(args.name, str), f"Expected str, got {type(args.name)}"
    assert isinstance(args.age, int), f"Expected int, got {type(args.age)}"
    assert isinstance(args.price, float), f"Expected float, got {type(args.price)}"

    # Verify values
    assert args.name == "John Doe", f"Expected name='John Doe', got {args.name}"
    assert args.age == 25, f"Expected age=25, got {args.age}"
    assert args.price == 99.99, f"Expected price=99.99, got {args.price}"

    print("✓ String and other types test passed\n")


def test_boolean_conversions():
    """Test various boolean conversion scenarios"""

    doc = """
    Test program with boolean values

    Usage:
        test.py --debug=<bool> --force=<bool>

    Options:
        --debug=<bool>  Debug mode
        --force=<bool>  Force operation
    """

    # Test different boolean representations
    test_cases = [
        (["--debug", "true", "--force", "1"], True, True),
        (["--debug", "false", "--force", "0"], False, False),
        (["--debug", "yes", "--force", "no"], True, False),
    ]

    for test_args, expected_debug, expected_force in test_cases:
        args = docopt_typed(doc, test_args)

        print(f"Boolean Test: {test_args}")
        print(f"  Debug: {args.debug} (type: {type(args.debug)})")
        print(f"  Force: {args.force} (type: {type(args.force)})")

        assert args.debug == expected_debug, f"Expected debug={expected_debug}, got {args.debug}"
        assert args.force == expected_force, f"Expected force={expected_force}, got {args.force}"

    print("✓ Boolean conversions test passed\n")


def test_attribute_access():
    """Test that arguments can be accessed as attributes"""

    doc = """
    Test program for attribute access

    Usage:
        test.py --speed=<int> --count=<float>

    Options:
        --speed=<int>   Speed value
        --count=<float> Count value
    """

    test_args = ["--speed", "42", "--count", "1.5"]
    args = docopt_typed(doc, test_args)

    print("=== Attribute Access Test ===")
    # These should work without errors
    speed_val = args.speed
    count_val = args.count

    print(f"Direct access: speed={speed_val}, count={count_val}")

    # Test that we can use attributes normally
    assert speed_val == 42, f"Expected speed=42, got {speed_val}"
    assert count_val == 1.5, f"Expected count=1.5, got {count_val}"

    print("✓ Attribute access test passed\n")
