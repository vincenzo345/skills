#!/usr/bin/env python3
import sys
from workbench import main

if __name__ == "__main__":
    sys.exit(main(["status", *sys.argv[1:]]))
