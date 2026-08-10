#!/usr/bin/env python
"""Verify that a normalised transcript preserved every word of its raw export.

Normalising a transcript is *restructuring*, never rewriting. This script is the
mechanical check on that contract: it compares the body word count and the sorted
body word multiset of the raw export against the normalised file, and exits
non-zero on any divergence, naming the words that went missing and the words that
appeared from nowhere.

Reordering is legal. Restructuring moves words between lines and between turns, so
only the multiset is compared, never the sequence.

THE BODY-EXTRACTION RULE
------------------------
Stated here in full, and applied literally. It is a rule, not a heuristic: if a
transcript does not match it, fix the transcript or the rule, do not add a special
case.

1. Scope.
   - raw file: the whole file is body.
   - normalised file: the body is everything AFTER the last line that is exactly
     `---`. A normalised file therefore carries its front matter and its flag list
     above that line, and its body contains no `---` line of its own.

2. Markers removed from the body of BOTH files before any word is counted, in this
   order:
   a. A line that is only a timestamp:      `0:08`, `12:04`, `1:02:56`
   b. An inline bracketed timestamp:        `[0:08]`, `[1:02:56]`
   c. A leading interjection quote marker:  `> ` at the start of a line
   d. A bold turn marker at line start:     `**Ada Wong:**`, `**Speaker A:**`
   e. A bracketed speaker id:               `[Speaker A]`
   f. A parenthesised speaker marker:       `(Ada Wong)`, `(Speaker A)`
      Capitalised words only, up to four, so `(laughs)` is text and stays.

3. Words. What survives is lowercased and cut into words on anything that is not a
   letter, a digit or an apostrophe. Leading and trailing apostrophes are dropped.
   Nothing else is normalised: fillers, mis-transcriptions and profanity are words
   like any other, and a preserved `windflex` is the point of the exercise.

Exit codes: 0 preserved, 1 diverged, 2 usage or read error.
"""

import argparse
import re
import sys
from collections import Counter

TIMESTAMP_LINE = re.compile(r"^\s*\d{1,2}:\d{2}(?::\d{2})?\s*$")
INLINE_TIMESTAMP = re.compile(r"\[\d{1,2}:\d{2}(?::\d{2})?\]")
PAREN_SPEAKER = re.compile(r"\((?:[A-Z][\w.'-]*)(?:\s+[A-Z0-9][\w.'-]*){0,3}\)")
BOLD_TURN = re.compile(r"^\s*\*\*[^*]{1,60}:\*\*")
BRACKET_SPEAKER = re.compile(r"\[Speaker [A-Z]\]")
LEADING_QUOTE = re.compile(r"^\s*>\s?")
SEPARATOR = re.compile(r"^\s*---\s*$")
WORD = re.compile(r"[a-z0-9']+")


def body_lines(text, role):
    """Apply rule 1: cut the file down to the lines that are body."""
    lines = text.splitlines()
    if role == "raw":
        return lines
    last_separator = -1
    for i, line in enumerate(lines):
        if SEPARATOR.match(line):
            last_separator = i
    if last_separator == -1:
        raise ValueError(
            "normalised file has no `---` separator, so its body cannot be found; "
            "a normalised transcript carries front matter and flags above a final "
            "`---` line"
        )
    return lines[last_separator + 1 :]


def strip_markers(line):
    """Apply rule 2 to one line."""
    if TIMESTAMP_LINE.match(line):
        return ""
    line = INLINE_TIMESTAMP.sub(" ", line)
    line = LEADING_QUOTE.sub("", line)
    line = BOLD_TURN.sub("", line)
    line = BRACKET_SPEAKER.sub(" ", line)
    line = PAREN_SPEAKER.sub(" ", line)
    return line


def words(text, role):
    """The body word multiset of one file, per the rule in the module docstring."""
    counter = Counter()
    for line in body_lines(text, role):
        for word in WORD.findall(strip_markers(line).lower()):
            word = word.strip("'")
            if word:
                counter[word] += 1
    return counter


def read(path):
    with open(path, "r", encoding="utf-8-sig", errors="replace") as handle:
        return handle.read()


def report(raw_counts, new_counts, out):
    missing = raw_counts - new_counts
    extra = new_counts - raw_counts
    raw_total = sum(raw_counts.values())
    new_total = sum(new_counts.values())

    out.write("raw body words:        %d\n" % raw_total)
    out.write("normalised body words: %d\n" % new_total)

    if not missing and not extra:
        out.write("\nPRESERVED. Word count and word multiset match.\n")
        return 0

    out.write("\nDIVERGED. The normalisation is rejected; redo it.\n")
    if missing:
        out.write("\nmissing from the normalised file (%d):\n" % sum(missing.values()))
        for word, count in sorted(missing.items()):
            out.write("  -%d  %s\n" % (count, word))
    if extra:
        out.write("\nnot in the raw export (%d):\n" % sum(extra.values()))
        for word, count in sorted(extra.items()):
            out.write("  +%d  %s\n" % (count, word))
    return 1


def main(argv=None):
    parser = argparse.ArgumentParser(
        description="Compare the body word multiset of a raw export and its normalisation.",
    )
    parser.add_argument("raw", nargs="?", help="the raw transcript export")
    parser.add_argument("normalised", nargs="?", help="the normalised transcript")
    parser.add_argument(
        "--rules",
        action="store_true",
        help="print the body-extraction rule this script applies, and exit",
    )
    args = parser.parse_args(argv)

    if args.rules:
        sys.stdout.write(__doc__ or "")
        return 0
    if not args.raw or not args.normalised:
        parser.error("both a raw file and a normalised file are required")

    try:
        raw_text = read(args.raw)
        new_text = read(args.normalised)
    except OSError as error:
        sys.stderr.write("cannot read: %s\n" % error)
        return 2

    try:
        raw_counts = words(raw_text, "raw")
        new_counts = words(new_text, "normalised")
    except ValueError as error:
        sys.stderr.write("%s\n" % error)
        return 2

    return report(raw_counts, new_counts, sys.stdout)


if __name__ == "__main__":
    sys.exit(main())
