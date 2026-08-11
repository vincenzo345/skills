#!/usr/bin/env python
"""Tests for verify_preservation.py. Dependency-free: `python test_verify_preservation.py`.

The fixture is synthetic and carries the format signature the real material has: a
timestamp on its own line, `(Name)` speaker markers, and a ` - ` backchannel lane
that cuts a sentence in half so its verb lands inside the other speaker's reply.

The calibration run against the one real sample is deliberately not here. That
sample is confidential and lives under `.scratch/`, which is gitignored. Run it by
hand when the sample is present.
"""

import io
import os
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import verify_preservation as vp

RAW = """0:00
(Ada Wong) Right, so a request comes in. - (Ben Choi) Mhm.
0:08
(Ada Wong) and we open a case against whoever sent (Ada Wong) it. Does that
0:16
(Ada Wong) ever - (Ben Choi) Yeah, sometimes. (Ada Wong) vary?
"""

NORMALISED = """---
source: raw.txt
provenance: in-the-room
labels: unverified
---

# Flags

- `merged-crosstalk` 0:16 - who says "vary"? Resolved: Ada Wong.

---

[0:00] **Ada Wong:** Right, so a request comes in. and we open a case against
whoever sent it. Does that ever vary?
> **Ben Choi:** Mhm.
> **Ben Choi:** Yeah, sometimes.
"""


def run(raw_text, normalised_text):
    """Run the script end to end on two temporary files. Returns (exit code, output)."""
    directory = tempfile.mkdtemp()
    raw_path = os.path.join(directory, "raw.txt")
    new_path = os.path.join(directory, "normalised.md")
    for path, text in ((raw_path, raw_text), (new_path, normalised_text)):
        with open(path, "w", encoding="utf-8") as handle:
            handle.write(text)
    captured = io.StringIO()
    stdout, sys.stdout = sys.stdout, captured
    try:
        code = vp.main([raw_path, new_path])
    finally:
        sys.stdout = stdout
    return code, captured.getvalue()


class TestPreservation(unittest.TestCase):
    def test_identical_body_passes(self):
        code, output = run(RAW, NORMALISED)
        self.assertEqual(code, 0, output)
        self.assertIn("PRESERVED", output)

    def test_deleted_word_is_reported_missing(self):
        code, output = run(RAW, NORMALISED.replace("Does that ever vary?", "Does that vary?"))
        self.assertEqual(code, 1)
        self.assertIn("missing from the normalised file", output)
        self.assertIn("ever", output)

    def test_added_word_is_reported_extra(self):
        code, output = run(RAW, NORMALISED.replace("a request comes in", "a new request comes in"))
        self.assertEqual(code, 1)
        self.assertIn("not in the raw export", output)
        self.assertIn("new", output)

    def test_reordering_is_legal(self):
        reordered = NORMALISED.replace(
            "Right, so a request comes in. and we open a case against\nwhoever sent it. Does that ever vary?",
            "Does that ever vary? Right, so a request comes in. and we open a\ncase against whoever sent it.",
        )
        code, output = run(RAW, reordered)
        self.assertEqual(code, 0, output)

    def test_markers_timestamps_and_header_are_excluded(self):
        """Different speaker markers, different timestamps, a whole header: still 0."""
        code, output = run(RAW, NORMALISED.replace("**Ada Wong:**", "**Speaker A:**").replace("[0:00]", "[9:99]".replace("9:99", "4:12")))
        self.assertEqual(code, 0, output)

    def test_flag_list_above_the_separator_is_not_body(self):
        """Words in the flag list are header, not body, however transcript-like."""
        noisy = NORMALISED.replace(
            "- `merged-crosstalk` 0:16 - who says \"vary\"? Resolved: Ada Wong.",
            "- `merged-crosstalk` 0:16 - who says \"vary\"? Resolved: Ada Wong.\n"
            "- `suspect-term` 0:08 - \"case\" heard as \"chase\". Resolved: case.",
        )
        code, output = run(RAW, noisy)
        self.assertEqual(code, 0, output)

    def test_normalised_file_without_a_separator_is_an_error(self):
        code, _ = run(RAW, "**Ada Wong:** Right, so a request comes in.\n")
        self.assertEqual(code, 2)

    def test_lowercasing_does_not_hide_a_deletion(self):
        code, output = run(RAW, NORMALISED.replace("Mhm.", ""))
        self.assertEqual(code, 1)
        self.assertIn("mhm", output)

    def test_mis_transcription_must_survive(self):
        """A suspect term is flagged, never corrected in the body."""
        raw = RAW.replace("a request comes in", "a windflex request comes in")
        normalised = NORMALISED.replace("a request comes in", "a winflex request comes in")
        code, output = run(raw, normalised)
        self.assertEqual(code, 1)
        self.assertIn("windflex", output)
        self.assertIn("winflex", output)

    def test_word_counts_are_printed_both_ways(self):
        _, output = run(RAW, NORMALISED)
        self.assertIn("raw body words:", output)
        self.assertIn("normalised body words:", output)


OTTER_RAW = """Ada Wong:  0:00
Right, so a request comes in, and we open a case. Does that ever vary?

Ben Choi:  0:16
Yeah, sometimes.
"""

VTT_RAW = """WEBVTT

00:00:00.000 --> 00:00:15.000
<v Ada Wong>Right, so a request comes in, and we open a case. Does that ever vary?

00:00:16.000 --> 00:00:18.000
<v Ben Choi>Yeah, sometimes.
"""

TWO_TURNS = """---
source: raw.txt
provenance: in-the-room
labels: unverified
{markers}---

# Flags

- none

---

[0:00] **Ada Wong:** Right, so a request comes in, and we open a case. Does that ever vary?
> **Ben Choi:** Yeah, sometimes.
"""


def normalised_with(*patterns):
    if not patterns:
        return TWO_TURNS.format(markers="")
    block = "raw_markers:\n" + "".join("  - '%s'\n" % pattern for pattern in patterns)
    return TWO_TURNS.format(markers=block)


class TestDeclaredMarkers(unittest.TestCase):
    """Rule 2a. The formats step 2 names - VTT, Otter, Fathom, Granola - are not one
    format, so the raw marker convention is declared rather than guessed."""

    def test_without_a_declaration_a_foreign_format_fails(self):
        """The failure this mechanism exists for: names and timestamps read as words."""
        code, output = run(OTTER_RAW, normalised_with())
        self.assertEqual(code, 1)
        self.assertIn("ada", output)
        self.assertIn("wong", output)

    def test_otter_style_passes_once_declared(self):
        code, output = run(
            OTTER_RAW,
            normalised_with(r"^[A-Z][\w.'-]*(?: [A-Z][\w.'-]*)*:\s*\d{1,2}:\d{2}\s*$"),
        )
        self.assertEqual(code, 0, output)
        self.assertIn("PRESERVED", output)

    def test_webvtt_passes_once_declared(self):
        code, output = run(
            VTT_RAW,
            normalised_with(
                r"^WEBVTT$",
                r"^\d{2}:\d{2}:\d{2}\.\d{3} --> .*$",
                r"<v [^>]+>",
            ),
        )
        self.assertEqual(code, 0, output)
        self.assertIn("PRESERVED", output)

    def test_declared_markers_apply_to_the_raw_file_only(self):
        """A marker that would eat normalised text leaves the normalised side alone."""
        code, output = run(OTTER_RAW, normalised_with(r"^[A-Z][\w.'-]*(?: [A-Z][\w.'-]*)*:\s*\d{1,2}:\d{2}\s*$", r"sometimes"))
        self.assertEqual(code, 1)
        self.assertIn("sometimes", output)

    def test_what_each_marker_removed_is_printed(self):
        _, output = run(
            OTTER_RAW,
            normalised_with(r"^[A-Z][\w.'-]*(?: [A-Z][\w.'-]*)*:\s*\d{1,2}:\d{2}\s*$"),
        )
        self.assertIn("raw markers declared: 1", output)
        self.assertIn("words removed", output)
        self.assertIn("Ada Wong:  0:00", output)

    def test_a_marker_that_matches_nothing_is_called_out(self):
        _, output = run(RAW, normalised_with(r"^NOSUCHTHING$"))
        self.assertIn("removed nothing", output)

    def test_a_greedy_marker_cannot_fake_a_pass(self):
        """Swallow the raw body and the normalised words have nowhere to come from."""
        code, output = run(RAW, normalised_with(r".*"))
        self.assertEqual(code, 1)
        self.assertIn("not in the raw export", output)

    def test_the_share_removed_is_printed(self):
        _, output = run(
            OTTER_RAW,
            normalised_with(r"^[A-Z][\w.'-]*(?: [A-Z][\w.'-]*)*:\s*\d{1,2}:\d{2}\s*$"),
        )
        self.assertIn("raw words (", output)

    def test_a_broken_regex_is_a_usage_error(self):
        code, _ = run(RAW, normalised_with(r"(unclosed"))
        self.assertEqual(code, 2)

    def test_an_inline_list_is_refused_rather_than_ignored(self):
        code, _ = run(RAW, TWO_TURNS.format(markers="raw_markers: ['^a$']\n"))
        self.assertEqual(code, 2)

    def test_no_declaration_leaves_the_built_in_rule_untouched(self):
        code, output = run(RAW, NORMALISED)
        self.assertEqual(code, 0, output)
        self.assertNotIn("raw markers declared", output)


class TestBodyRule(unittest.TestCase):
    def test_parenthesised_lowercase_text_is_not_a_speaker_marker(self):
        self.assertEqual(vp.strip_markers("(laughs) yes").strip(), "(laughs) yes")

    def test_parenthesised_name_is_a_speaker_marker(self):
        self.assertEqual(vp.strip_markers("(Ada Wong) yes").strip(), "yes")

    def test_timestamp_only_line_is_dropped(self):
        self.assertEqual(vp.strip_markers("1:02:56"), "")

    def test_raw_body_is_the_whole_file(self):
        self.assertEqual(len(vp.body_lines("a\n---\nb\n", "raw")), 3)


if __name__ == "__main__":
    unittest.main(verbosity=2)
