"""Unit tests for eea.plotly utility modules

These tests cover pure functions that don't require Plone context:
- utils: setProperty, delProperty, sanitizeVisualization, getLink, getLinkHTML, isExpanded
- io_csv: CsvWriter, CsvReader
- io_json: JSONEncoder
"""

import unittest
import json
import decimal
import io

from eea.plotly.utils import (
    setProperty,
    delProperty,
    sanitizeVisualization,
    getLink,
    getLinkHTML,
    isExpanded,
)
from eea.plotly.io_csv import CsvWriter, CsvReader, NULL
from eea.plotly.io_json import JSONEncoder


class TestSetProperty(unittest.TestCase):
    """Tests for setProperty function"""

    def test_set_value_not_none(self):
        obj = {}
        setProperty(obj, "key", "value")
        self.assertEqual(obj["key"], "value")

    def test_set_value_none(self):
        obj = {}
        setProperty(obj, "key", None)
        self.assertNotIn("key", obj)

    def test_set_overwrites(self):
        obj = {"key": "old"}
        setProperty(obj, "key", "new")
        self.assertEqual(obj["key"], "new")

    def test_set_integer(self):
        obj = {}
        setProperty(obj, "count", 42)
        self.assertEqual(obj["count"], 42)

    def test_set_empty_string(self):
        obj = {}
        setProperty(obj, "key", "")
        self.assertEqual(obj["key"], "")


class TestDelProperty(unittest.TestCase):
    """Tests for delProperty function"""

    def test_delete_existing(self):
        obj = {"key": "value"}
        delProperty(obj, "key")
        self.assertNotIn("key", obj)

    def test_delete_nonexistent(self):
        obj = {}
        delProperty(obj, "key")  # should not raise

    def test_delete_other_keys_preserved(self):
        obj = {"a": 1, "b": 2}
        delProperty(obj, "a")
        self.assertEqual(obj, {"b": 2})


class TestSanitizeVisualization(unittest.TestCase):
    """Tests for sanitizeVisualization function"""

    def test_empty_visualization(self):
        result = sanitizeVisualization({})
        self.assertEqual(result["data"], [])
        self.assertEqual(result["layout"], {})
        self.assertEqual(result["columns"], [])
        self.assertEqual(result["dataSources"], {})

    def test_with_data(self):
        v = {"data": [{"x": [1, 2], "y": [3, 4]}]}
        result = sanitizeVisualization(v)
        self.assertEqual(result["data"], [{"x": [1, 2], "y": [3, 4]}])

    def test_with_chart_data_backward_compat(self):
        v = {"chartData": {"data": [{"x": [1]}], "layout": {"title": "test"}}}
        result = sanitizeVisualization(v)
        self.assertEqual(result["data"], [{"x": [1]}])
        self.assertEqual(result["layout"], {"title": "test"})

    def test_with_layout(self):
        v = {"layout": {"title": "My Chart"}}
        result = sanitizeVisualization(v)
        self.assertEqual(result["layout"], {"title": "My Chart"})

    def test_with_columns(self):
        v = {"columns": [{"name": "col1"}]}
        result = sanitizeVisualization(v)
        self.assertEqual(result["columns"], [{"name": "col1"}])

    def test_data_sources_merge(self):
        v = {
            "data_source": {"src1": "url1"},
            "dataSources": {"src2": "url2"},
        }
        result = sanitizeVisualization(v)
        self.assertEqual(result["dataSources"], {"src1": "url1", "src2": "url2"})

    def test_optional_properties_set(self):
        v = {
            "provider_url": "https://example.com",
            "variation": "bar",
            "filters": {"field": "value"},
            "id": "viz-1",
            "type": "plotly",
            "label": "My Viz",
        }
        result = sanitizeVisualization(v)
        self.assertEqual(result["provider_url"], "https://example.com")
        self.assertEqual(result["variation"], "bar")
        self.assertEqual(result["filters"], {"field": "value"})
        self.assertEqual(result["id"], "viz-1")
        self.assertEqual(result["type"], "plotly")
        self.assertEqual(result["label"], "My Viz")

    def test_optional_properties_none_not_set(self):
        v = {"provider_url": None, "variation": None}
        result = sanitizeVisualization(v)
        self.assertNotIn("provider_url", result)
        self.assertNotIn("variation", result)

    def test_default_empty_dict(self):
        result = sanitizeVisualization()
        self.assertIsNotNone(result)


class TestGetLink(unittest.TestCase):
    """Tests for getLink function"""

    def test_localhost_link(self):
        result = getLink("http://localhost:8080/Plone/page")
        self.assertEqual(result, "/Plone/page")

    def test_external_link(self):
        result = getLink("https://example.com/page")
        self.assertEqual(result, "https://example.com/page")

    def test_relative_path(self):
        result = getLink("/Plone/page")
        self.assertEqual(result, "/Plone/page")


class TestGetLinkHTML(unittest.TestCase):
    """Tests for getLinkHTML function"""

    def test_with_text(self):
        result = getLinkHTML("https://example.com", "Click here")
        self.assertEqual(result, '<a href="https://example.com" target="_blank">Click here</a>')

    def test_without_text(self):
        result = getLinkHTML("https://example.com")
        self.assertEqual(result, '<a href="https://example.com" target="_blank">https://example.com</a>')

    def test_empty_url(self):
        result = getLinkHTML("")
        self.assertEqual(result, "")

    def test_none_url(self):
        result = getLinkHTML(None)
        self.assertIsNone(result)


class TestIsExpanded(unittest.TestCase):
    """Tests for isExpanded function"""

    def test_expanded(self):
        class FakeRequest:
            form = {"expand.visualization": "1"}
        self.assertTrue(isExpanded(FakeRequest()))

    def test_not_expanded(self):
        class FakeRequest:
            form = {}
        self.assertFalse(isExpanded(FakeRequest()))


class TestCsvWriter(unittest.TestCase):
    """Tests for CsvWriter class"""

    def test_write_row_with_none(self):
        output = io.StringIO()
        writer = CsvWriter(output)
        writer.writerow(["a", None, "b"])
        output.seek(0)
        self.assertEqual(output.read().strip(), "a,NULL,b")

    def test_write_row_no_none(self):
        output = io.StringIO()
        writer = CsvWriter(output)
        writer.writerow(["a", "b", "c"])
        output.seek(0)
        self.assertEqual(output.read().strip(), "a,b,c")

    def test_write_rows(self):
        output = io.StringIO()
        writer = CsvWriter(output)
        writer.writerows([["a", None], [None, "b"]])
        output.seek(0)
        lines = output.read().strip().split("\n")
        self.assertEqual(lines[0].strip(), "a,NULL")
        self.assertEqual(lines[1].strip(), "NULL,b")

    def test_write_empty_row(self):
        output = io.StringIO()
        writer = CsvWriter(output)
        writer.writerow([])
        output.seek(0)
        self.assertEqual(output.read().strip(), "")


class TestCsvReader(unittest.TestCase):
    """Tests for CsvReader class"""

    def test_read_row_with_null(self):
        input_data = "a,NULL,b\n"
        reader = CsvReader(io.StringIO(input_data))
        rows = list(reader)
        self.assertEqual(rows, [["a", None, "b"]])

    def test_read_row_no_null(self):
        input_data = "a,b,c\n"
        reader = CsvReader(io.StringIO(input_data))
        rows = list(reader)
        self.assertEqual(rows, [["a", "b", "c"]])

    def test_read_multiple_rows(self):
        input_data = "a,b\nNULL,c\n"
        reader = CsvReader(io.StringIO(input_data))
        rows = list(reader)
        self.assertEqual(len(rows), 2)
        self.assertEqual(rows[0], ["a", "b"])
        self.assertEqual(rows[1], [None, "c"])

    def test_null_constant(self):
        self.assertEqual(NULL, "NULL")


class TestJSONEncoder(unittest.TestCase):
    """Tests for JSONEncoder class"""

    def test_encode_decimal(self):
        result = json.dumps({"value": decimal.Decimal("3.14")}, cls=JSONEncoder)
        self.assertEqual(result, '{"value": "3.14"}')

    def test_encode_regular_types(self):
        result = json.dumps({"int": 42, "str": "hello"}, cls=JSONEncoder)
        self.assertEqual(result, '{"int": 42, "str": "hello"}')

    def test_encode_nested_decimal(self):
        data = {"chart": {"value": decimal.Decimal("10.5")}}
        result = json.dumps(data, cls=JSONEncoder)
        self.assertEqual(result, '{"chart": {"value": "10.5"}}')

    def test_encode_list_with_decimal(self):
        data = [1, decimal.Decimal("2.5"), 3]
        result = json.dumps(data, cls=JSONEncoder)
        self.assertEqual(result, '[1, "2.5", 3]')


if __name__ == "__main__":
    unittest.main()