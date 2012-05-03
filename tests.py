#!/usr/bin/python

"""Test cases for grading scripts

Testing of grading scripts
"""

__author__ = "Fil Zembowicz (fil@filosophy.org)"

import unittest

class testTextHelpers(unittest.TestCase):
  """A test class for text processing utility functions"""

  def test_strip(self):
    from utils.line_features import strip
    self.assertEqual(strip("    int a = 3;   "), "int a = 3;")
    self.assertEqual(strip("    int a = 3; // a is set to 3   "), "int a = 3;")
    self.assertEqual(strip("    int a = 3; /* a is set to 3 */  "), "int a = 3;")

  def test_get_indent(self):
    from utils.line_features import get_indent
    self.assertEqual(get_indent("int a = 3; "), 0)
    self.assertEqual(get_indent(" int a = 3; "), 1)
    self.assertEqual(get_indent("    int a = 3; "), 4)
    self.assertEqual(get_indent("\t\tint a = 3; "), 2)

  def test_is_comment(self):
    from utils.line_features import is_comment
    self.assertEqual(is_comment("  // comment "), True)
    self.assertEqual(is_comment("  /* comment "), True)
    self.assertEqual(is_comment("  Something(); // comment "), False)
    self.assertEqual(is_comment("  Something();  "), False)

  def test_is_paren(self):
    from utils.line_features import is_paren
    self.assertEqual(is_paren("     {   "), True)
    self.assertEqual(is_paren("}"), True)
    self.assertEqual(is_paren("(){"), False)
    self.assertEqual(is_paren("    "), False)

  def test_is_whitespace_line(self):
    from utils.line_features import is_whitespace_line
    self.assertEqual(is_whitespace_line(""), True)
    self.assertEqual(is_whitespace_line("\t\t  \t"), True)
    self.assertEqual(is_whitespace_line("\t\t {\t"), False)

  def test_is_incomplete_statement(self):
    from utils.line_features import is_incomplete_statement
    self.assertEqual(is_incomplete_statement("for(int i = 0; i < 10; i++)"), True)
    self.assertEqual(is_incomplete_statement(""), True)
    self.assertEqual(is_incomplete_statement("printf('hey');"), False)

class testCodeHelpers(unittest.TestCase):
  """A test class for code parsing utilities"""
  
  def test_linebreak_indices(self):
    from annotator import get_linebreak_indices
    a = "Begin\n\nThis is the third line\nAnd this is the fourth\nEnd of file"
    indices = get_linebreak_indices(a)
    self.assertEqual(len(indices), 4)
    self.assertEqual(indices, [5, 6, 29, 52])

class testIndent(unittest.TestCase):
  """Testing indentation calculation"""

  def setUp(self):
    pass

class testMustPass(unittest.TestCase):
  """Testing that "perfect" assignments pass all tests"""

  def setUp(self):
    pass

def suite():
  suite = unittest.TestSuite()
  suite.addTest(unittest.makeSuite(testTextHelpers))
  suite.addTest(unittest.makeSuite(testCodeHelpers))
  suite.addTest(unittest.makeSuite(testIndent))
  suite.addTest(unittest.makeSuite(testMustPass))
  return suite

def main():
  unittest.TextTestRunner(verbosity=2).run(suite())

if __name__ == "__main__":
  main()
