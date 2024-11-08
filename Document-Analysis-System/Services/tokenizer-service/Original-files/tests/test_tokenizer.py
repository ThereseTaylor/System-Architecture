# File: test_text_tokenizer.py
import unittest
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "modules"))

from modules.tokenizer import tokenize_text

class TestTextTokenizer(unittest.TestCase):

    def test_tokenize_text(self):
        # Test case 1
        text = "Hello World"
        result = tokenize_text(text)
        self.assertEqual(result, ["Hello", "World"], "Failed for input: 'Hello World'")

        # Test case 2
        text = "Python is awesome"
        result = tokenize_text(text)
        self.assertEqual(result, ["Python", "is", "awesome"], "Failed for input: 'Python is awesome'")

        # Test case 3
        text = "  This   is   a   test  "
        result = tokenize_text(text)
        self.assertEqual(result, ["This", "is", "a", "test"], "Failed for input with extra spaces")

        # Test case 4
        text = ""
        result = tokenize_text(text)
        self.assertEqual(result, [], "Failed for empty input")

if __name__ == '__main__':
    unittest.main()
