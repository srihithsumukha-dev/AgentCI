import sys
import unittest
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SAMPLE_PROJECT = PROJECT_ROOT / "benchmarks" / "sample_project"
sys.path.insert(0, str(SAMPLE_PROJECT))

from parse_items_broken import parse


class TestBrokenParseItems(unittest.TestCase):
    def test_empty_list_returns_none(self):
        self.assertIsNone(parse([]))

    def test_non_empty_list_returns_first_item(self):
        self.assertEqual(parse(["hello", "world"]), "hello")


if __name__ == "__main__":
    unittest.main()