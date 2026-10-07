#!/usr/bin/env python3
import sys
from workbench import main

if __name__ == "__main__":
    sys.exit(main(["next", *sys.argv[1:]]))
