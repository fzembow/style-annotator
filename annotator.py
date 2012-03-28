#!/usr/bin/python

"""Utilities for processing .c files for grading

Miscellaneous utilities for assisting in processing assignments
"""

__author__ = "Fil Zembowicz (fil@filosophy.org)"

import os, sys, re
from subprocess import Popen, PIPE
from features import test_feature_list, production_feature_list, get_indent_levels, get_ignore_lines, FeatureIndentation, strip
import features

#
# INPUT MANIPULATION
#

class Code:
  """Wrapper for holding information about a single file of code"""

  def __init__(self, text=None, filename=None):
    if filename == None and text == None:
      raise AttributeError("need a filename or text")
      return
    if filename:
      self.filename = filename
      self.text = get_text(filename)
    elif text:
      self.text = text
    self.lines = self.text.split("\n")
    self.linebreak_indices = get_linebreak_indices(self.text)
    self.levels = get_indent_levels(self.lines)
    self.ignore_lines = get_ignore_lines(self.lines)

    self.stripped = [] # lines without whitespace or comments
    for line_no, line in enumerate(self.lines):
      if self.ignore_lines[line_no]:
        self.stripped.append("")
      else:
        self.stripped.append(strip(line))

  def get_lines_for_span(self, span):
    """Given a span of character indices (start, end) into the code, finds the line nos"""
    start, end = span
    startline = 0
    for line_index, char_index in enumerate(self.linebreak_indices):
      if char_index > start:
        startline = line_index 
      if char_index > end:
        return (startline, line_index)

    return startline, len(self.linebreak_indices)

  def get_ast(self):
    if not self.ast:
      self.ast = get_ast_from_file(self.filename)
    return self.ast

  ast = property(get_ast)

def get_linebreak_indices(text):
  """Finds the indices in text at which linebreaks happen

  This is useful to find what lines a particular text appears on"""
  chunks = re.split(r"(\n)", text)
  chars = 0
  indices = []
  for index, chunk in enumerate(chunks):
    if index % 2 == 1: #newline
      indices.append(chars)
    chars += len(chunk)
  return indices

def get_text(filename):
  """Reads a file and returns the text"""
  return open(filename, "rU").read()

def get_cpp(filename, cpp_path='cpp', cpp_args=''):
  """Runs C preprocessor on a file and returns the text"""
  path_list = [cpp_path]
  if isinstance(cpp_args, list):
    path_list += cpp_args
  elif cpp_args != '':
    path_list += [cpp_args]
  path_list += [filename]
  pipe = Popen( path_list,
                stdout=PIPE,
                universal_newlines=True)
  return pipe.communicate()[0]

#
# FILE MANIPULATION
#

def annotate(code, feature_list=production_feature_list):
  annotations = {}
  for feature in feature_list:
    f = feature()
    try: 
      f.compute(code, annotations)
    except features.TimedOutExc as e:
      print "Timed out execution"
  return annotations

def find_c_files(base):
  """Yields the (full) filenames of each .c file in a dir"""
  for path, dirs, files in os.walk(base):
    for filename in files:
      abspath = os.path.abspath(os.path.join(path, filename))
      ext = os.path.splitext(abspath)[1]
      if ext == ".c":
        yield abspath

def try_features(base):
  for c_file in find_c_files(base):
    try:
      code = Code(filename=c_file)
    except features.TimedOutExc:
      print "timed out parsing code"
      continue
    annotations = annotate(code, feature_list=test_feature_list)
    if annotations:
      print c_file
      print annotations
      print

def show_indent(f):
  code = get_text(f)
  lines = code.split("\n")
  levels = get_indent_levels(lines)
  errors = FeatureIndentation(code)
  ignore = get_ignore_lines(lines)
  for line_no, line in enumerate(lines):
    
    if line_no in errors:
      print
      print
      for i in range(line_no - 3, line_no):
        print str(levels[i]) + "\t" + lines[i]
      print str(levels[line_no]) + "\t" + line
      print " ^^^ "
      print errors[line_no]
      print
      for i in range(line_no+1, line_no+3):
        print str(levels[i]) + "\t" + lines[i]
      print
      print
 
def main():
  if len(sys.argv) > 1:
    command = sys.argv[1]
    if command == "test":
      try_features("/home/fzembow/psets/")
    elif command == "indent":
      filename = sys.argv[2]
      show_indent(filename)

if __name__ == "__main__":
  main()
