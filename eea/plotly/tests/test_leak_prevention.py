"""Unit tests for chart-summary leak prevention.

Plain unit tests, no Plone bootstrap. Cover the three guards added after
a summary leaked phrases like "early 2010s through early 2030s":

1. Numeric arrays must never reach the LLM raw, regardless of length.
2. Year-like string arrays ("2012", "2013", ...) must not leak first/last
   samples either.
3. ``clean_layout`` must strip axis range / tickvals / tick0 / etc.
"""

import json
import unittest

from eea.plotly.context_providers import (
    _is_numeric_list,
    _looks_like_year_strings,
    _summarize_array,
    _truncate_data_sources,
    _truncate_trace,
)
from eea.plotly.prompts import AXIS_LEAKY_KEYS, IRRELEVANT_LAYOUT_KEYS, clean_layout


class TestNumericDetection(unittest.TestCase):

    def test_ints(self):
        self.assertTrue(_is_numeric_list([1, 2, 3]))

    def test_floats(self):
        self.assertTrue(_is_numeric_list([1.5, 2.5]))

    def test_mixed_int_float(self):
        self.assertTrue(_is_numeric_list([1, 2.0, 3]))

    def test_bool_excluded(self):
        # bool is a subclass of int but is not numeric data.
        self.assertFalse(_is_numeric_list([True, False, True]))

    def test_strings_excluded(self):
        self.assertFalse(_is_numeric_list(["1", "2"]))

    def test_mixed_excluded(self):
        self.assertFalse(_is_numeric_list([1, "x"]))

    def test_empty_false(self):
        self.assertFalse(_is_numeric_list([]))


class TestYearStringDetection(unittest.TestCase):

    def test_recent_years(self):
        self.assertTrue(_looks_like_year_strings(["2012", "2013", "2014"]))

    def test_full_range(self):
        self.assertTrue(_looks_like_year_strings(["1800", "2200"]))

    def test_three_digit_excluded(self):
        self.assertFalse(_looks_like_year_strings(["999", "2000"]))

    def test_non_year_strings(self):
        self.assertFalse(_looks_like_year_strings(["foo", "bar"]))

    def test_out_of_range(self):
        self.assertFalse(_looks_like_year_strings(["1799", "2201"]))

    def test_ints_not_year_strings(self):
        # _is_numeric_list handles ints. Year-string check is for strs only.
        self.assertFalse(_looks_like_year_strings([2012, 2013]))


class TestSummarizeArray(unittest.TestCase):

    def test_numeric_no_quant_leak(self):
        out = _summarize_array([2012, 2013, 2014, 2015, 2016])
        self.assertEqual(out, "[5 numeric values]")
        self.assertNotIn("2012", out)
        self.assertNotIn("2016", out)

    def test_year_strings_no_leak(self):
        out = _summarize_array(["2012", "2013", "2014", "2030", "2031", "2032"])
        self.assertEqual(out, "[6 year-like values]")
        self.assertNotIn("2012", out)
        self.assertNotIn("2032", out)

    def test_categorical_keeps_samples(self):
        out = _summarize_array(["DE", "FR", "IT", "ES", "PL"])
        # Country codes are useful retrieval keywords — kept.
        self.assertIn("DE", out)


class TestTruncateTrace(unittest.TestCase):

    def test_small_year_axis_summarized(self):
        # Year axis of ~20 points was previously inlined verbatim.
        trace = {
            "type": "scatter",
            "name": "EU GDP",
            "x": list(range(2012, 2033)),  # 21 ints
            "y": [1.1 * i for i in range(21)],
        }
        out = _truncate_trace(trace)
        self.assertEqual(out["type"], "scatter")
        self.assertEqual(out["name"], "EU GDP")
        self.assertEqual(out["x"], "[21 numeric values]")
        self.assertEqual(out["y"], "[21 numeric values]")
        # Sanity: serialize and verify no year token leaked.
        rendered = json.dumps(out)
        for year in range(2010, 2035):
            self.assertNotIn(str(year), rendered)

    def test_small_year_string_axis_summarized(self):
        trace = {"type": "bar", "x": ["2012", "2013", "2030", "2031", "2032"]}
        out = _truncate_trace(trace)
        self.assertEqual(out["x"], "[5 year-like values]")
        rendered = json.dumps(out)
        for year in ["2012", "2013", "2030", "2031", "2032"]:
            self.assertNotIn(year, rendered)

    def test_short_categorical_passes_through(self):
        trace = {"type": "bar", "x": ["DE", "FR", "IT"]}
        out = _truncate_trace(trace)
        self.assertEqual(out["x"], ["DE", "FR", "IT"])


class TestTruncateDataSources(unittest.TestCase):

    def test_small_numeric_column_summarized(self):
        ds = {"Year": list(range(2012, 2033)), "Country": ["DE", "FR"]}
        out = _truncate_data_sources(ds)
        self.assertEqual(out["Year"], "[21 numeric values]")
        self.assertEqual(out["Country"], ["DE", "FR"])


class TestCleanLayout(unittest.TestCase):

    def test_cosmetic_stripped(self):
        layout = {"paper_bgcolor": "white", "title": {"text": "Chart"}}
        out = clean_layout(layout)
        self.assertNotIn("paper_bgcolor", out)
        self.assertIn("title", out)
        self.assertIn("paper_bgcolor", IRRELEVANT_LAYOUT_KEYS)

    def test_axis_range_stripped(self):
        layout = {
            "xaxis": {
                "title": {"text": "Year"},
                "range": [2012, 2032],
                "tickvals": [2012, 2016, 2020, 2024, 2028, 2032],
                "type": "linear",
            },
            "yaxis": {
                "title": {"text": "Value"},
                "range": [0, 100],
            },
        }
        out = clean_layout(layout)
        self.assertIn("xaxis", out)
        self.assertIn("title", out["xaxis"])
        self.assertEqual(out["xaxis"]["type"], "linear")
        # Leaky keys gone.
        self.assertNotIn("range", out["xaxis"])
        self.assertNotIn("tickvals", out["xaxis"])
        self.assertNotIn("range", out["yaxis"])
        # All known leaky keys are in the strip list.
        for k in ("range", "tickvals", "tick0", "dtick", "tickformat"):
            self.assertIn(k, AXIS_LEAKY_KEYS)

    def test_secondary_axes_also_cleaned(self):
        layout = {
            "xaxis2": {"range": [2012, 2032], "title": {"text": "x2"}},
            "yaxis3": {"tickvals": [0, 50, 100], "type": "linear"},
        }
        out = clean_layout(layout)
        self.assertNotIn("range", out["xaxis2"])
        self.assertNotIn("tickvals", out["yaxis3"])

    def test_no_year_leak_in_serialized_layout(self):
        layout = {
            "title": {"text": "EU vs Country GDP"},
            "xaxis": {"range": [2012, 2032], "tickvals": list(range(2012, 2033))},
            "yaxis": {"range": [0, 100]},
        }
        rendered = json.dumps(clean_layout(layout))
        for year in range(2010, 2035):
            self.assertNotIn(str(year), rendered)
