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
Stated here in full, and applied literally. Two files, two marker sets, and they
never mix. The raw export has no fixed shape, so its markers are **declared**. The
normalised file has the one shape `/to-record` defines, so its markers are **built
in**. Neither set touches the other file.

1. Scope.
   - raw file: the whole file is body.
   - normalised file: the body is everything AFTER the last line that is exactly
     `---`. A normalised file therefore carries its front matter and its flag list
     above that line, and its body contains no `---` line of its own.

2a. Declared raw markers. The only thing removed from the RAW file.

   Export formats are endless, so the raw file's marker convention is declared
   rather than guessed. The normalised front matter carries a `raw_markers:` block
   list of regular expressions, and each one is removed from every raw line.

       ---
       source: meeting.vtt
       provenance: in-the-room
       labels: unverified
       raw_markers:
         - '^WEBVTT$'
         - '^\\d{2}:\\d{2}:\\d{2}\\.\\d{3} --> .*$'
         - '<v [^>]+>'
       ---

   **Nothing is built in on this side, and that is the rule rather than a gap.** A
   built-in pattern removes words nobody declared, and whatever it removes it also
   hides: content the normalisation dropped is then deleted from *both* sides of
   the comparison and the check still passes. A `(New York)` office spoken aloud
   and lost in the normalisation reads as preserved. The designed-against format
   is no exception and declares like every other:

         - '^\\s*\\d{1,2}:\\d{2}(?::\\d{2})?\\s*$'
         - '\\((?:[A-Z][\\w.''-]*)(?:\\s+[A-Z0-9][\\w.''-]*){0,3}\\)'

   An apostrophe inside a single-quoted pattern is doubled, the YAML way.

   Declare nothing and every speaker name and timestamp counts as a word, so the
   run fails loudly with those words listed as missing. That is the intended
   failure. A marker convention you have not stated is one you have not worked out.

   Patterns are matched per line, in the order declared, and each is reported with
   its match count, the words it removed and a sample of what it matched. The
   report is the control, and there is no threshold on it. A marker set that
   swallows the whole raw body cannot fake a pass - the normalised words then have
   nowhere to come from and are reported as `not in the raw export`. What a
   threshold could not catch is a marker naming one content word, and what catches
   that is reading the declaration: it stands in the front matter of the artifact
   and prints on every run. Declare a marker convention, never a word.

2b. Built-in normalised markers. Removed from the NORMALISED file only. This skill
   defines that file's shape, so these three are fixed:
   a. An inline bracketed timestamp:        `[0:08]`, `[1:02:56]`
   b. A leading interjection quote marker:  `> ` at the start of a line
   c. A bold turn marker at line start:     `**Ada Wong:**`, `**Speaker A:**`

   A timestamp on its own line, a `(Ada Wong)` speaker marker, a `[Speaker A]` id:
   those are export conventions rather than this skill's output format. They
   belong to 2a, and they are never removed from the normalised file.

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

INLINE_TIMESTAMP = re.compile(r"\[\d{1,2}:\d{2}(?::\d{2})?\]")
BOLD_TURN = re.compile(r"^\s*\*\*[^*]{1,60}:\*\*")
LEADING_QUOTE = re.compile(r"^\s*>\s?")
SEPARATOR = re.compile(r"^\s*---\s*$")
WORD = re.compile(r"[a-z0-9']+")

MARKERS_KEY = re.compile(r"^raw_markers:\s*(.*)$")
LIST_ITEM = re.compile(r"^\s+-\s+(.*\S)\s*$")


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


def unquote(value):
    """Strip the surrounding quotes, and undouble a quote escaped the YAML way."""
    if len(value) > 1 and value[0] == value[-1] and value[0] in "'\"":
        return value[1:-1].replace(value[0] * 2, value[0])
    return value


def declared_markers(text):
    """Apply rule 2a: read `raw_markers:` out of the normalised front matter."""
    lines = text.splitlines()
    if not lines or not SEPARATOR.match(lines[0]):
        return []
    end = None
    for i in range(1, len(lines)):
        if SEPARATOR.match(lines[i]):
            end = i
            break
    if end is None:
        return []

    patterns = []
    collecting = False
    for line in lines[1:end]:
        key = MARKERS_KEY.match(line)
        if key:
            if key.group(1).strip():
                raise ValueError(
                    "`raw_markers:` takes a block list, one pattern per line, "
                    "indented and introduced by `- `; an inline list is not read"
                )
            collecting = True
            continue
        if not collecting:
            continue
        item = LIST_ITEM.match(line)
        if item:
            patterns.append(unquote(item.group(1)))
        elif line.strip():
            collecting = False
    return patterns


def compile_markers(patterns):
    compiled = []
    for pattern in patterns:
        try:
            compiled.append((pattern, re.compile(pattern)))
        except re.error as error:
            raise ValueError("raw_markers pattern %s is not a regex: %s" % (pattern, error))
    return compiled


def apply_markers(line, markers, tally=None):
    """Apply rule 2a to one raw line, recording what each marker removed."""
    for index, (_, regex) in enumerate(markers):
        if tally is None:
            line = regex.sub(" ", line)
        else:
            bucket = tally[index]

            def swallow(match, bucket=bucket):
                bucket.append(match.group(0))
                return " "

            line = regex.sub(swallow, line)
    return line


def strip_normalised_markers(line):
    """Apply rule 2b to one line of the normalised file. Never to the raw file."""
    line = INLINE_TIMESTAMP.sub(" ", line)
    line = LEADING_QUOTE.sub("", line)
    line = BOLD_TURN.sub("", line)
    return line


def words(text, role, markers=(), tally=None):
    """The body word multiset of one file, per the rule in the module docstring.

    Each role gets its own marker set and only its own: the raw file is cut by
    what `raw_markers:` declares, the normalised file by the built-in three.
    """
    counter = Counter()
    for line in body_lines(text, role):
        if role == "raw":
            line = apply_markers(line, markers, tally)
        else:
            line = strip_normalised_markers(line)
        for word in WORD.findall(line.lower()):
            word = word.strip("'")
            if word:
                counter[word] += 1
    return counter


def read(path):
    with open(path, "r", encoding="utf-8-sig", errors="replace") as handle:
        return handle.read()


def report_markers(markers, tally, before, after, out):
    """Show what each declared marker removed. Reading this is the control on 2a."""
    out.write("raw markers declared: %d\n" % len(markers))
    if not markers:
        out.write(
            "  Nothing is removed from the raw export. Every timestamp and every\n"
            "  speaker name in it counts as a word.\n\n"
        )
        return
    for (pattern, _), matches in zip(markers, tally):
        out.write("  %s\n" % pattern)
        if not matches:
            out.write("      0 matches. This marker removed nothing; check it.\n")
            continue
        removed = sum(len(WORD.findall(match.lower())) for match in matches)
        distinct = list(dict.fromkeys(match.strip() for match in matches))[:4]
        out.write(
            "      %d matches, %d words removed. e.g. %s\n"
            % (len(matches), removed, ", ".join('"%s"' % text for text in distinct))
        )
    share = (100.0 * (before - after) / before) if before else 0.0
    out.write(
        "  markers removed %d of %d raw words (%.0f%%). Read that share: a verbose\n"
        "  cue format runs high, a chat log should not.\n\n" % (before - after, before, share)
    )


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
        markers = compile_markers(declared_markers(new_text))
        undeclared = words(raw_text, "raw")
        tally = [[] for _ in markers]
        raw_counts = words(raw_text, "raw", markers, tally)
        new_counts = words(new_text, "normalised")
    except ValueError as error:
        sys.stderr.write("%s\n" % error)
        return 2

    report_markers(
        markers, tally, sum(undeclared.values()), sum(raw_counts.values()), sys.stdout
    )

    return report(raw_counts, new_counts, sys.stdout)


if __name__ == "__main__":
    sys.exit(main())
