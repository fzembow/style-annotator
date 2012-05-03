
import re

def strip(line):
  """Strips all leading / training whitespace / comments from a line"""
  return re.match(r"(.*?)(?://|/\*|$)",line).groups()[0].strip()

def is_comment(line):
  """Whether a line is a comment"""
  return re.match(r"^ *?(?://|/\*)",line) is not None

def is_paren(line):
  """Finds whether a line is a paren"""
  return re.match("^\s*[\{\}]\s*$", line) is not None

def is_whitespace_line(line):
  """Finds whether a line is empty"""
  return re.match("^\s*$", line) is not None

def get_indent(line):
  """Finds the length of leading whitespace"""
  return re.match(r"\s*", line).end()

def is_whitespace_line(line):
  """Finds whether a line is empty"""
  return re.match("^\s*$", line) is not None

def is_incomplete_statement(line):
  """Whether line ends in semicolon"""
  return re.search(r";\s*$", line) is None

def get_num_statements(line):
  """Finds how many statements are in a line, counting semicolons"""
  #TODO(fil)
  num_statements = 0
  return num_statements

