#!/usr/bin/env python3
import sys


def main(argv=None):
    args = list(sys.argv[1:] if argv is None else argv)
    quiet = "--quiet" in args
    args = [arg for arg in args if arg != "--quiet"]
    if len(args) != 1:
        print("error: expected exactly one integer argument", file=sys.stderr)
        return 2
    try:
        value = int(args[0])
    except ValueError:
        print(f"error: not an integer: {args[0]!r}", file=sys.stderr)
        return 2
    if not quiet:
        print(value * value)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
