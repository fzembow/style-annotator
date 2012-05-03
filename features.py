#!/usr/bin/python

"""Style (readability) features of .c code
  

Features return None if the code has the feature, or
a dict of {line: error} if missing. Line numbers always 0-based
"""

__author__ = "Fil Zembowicz (fil@filosophy.org)"

# TODO: ignore indentation within multiline comments
# Allow multi-line params
# 
# Running features returns either the number of stylistic features
# found of each type or a ParseError if parsing fails

LINE_LENGTH_THRESHOLD = 120 # when to warn about too wide lines
MAX_WHITESPACE_LINES = 3 # most consecutive whitespace lines to allow
MAX_NON_WHITESPACE_LINES = 8 # most consecutive non-whitespace lines to allow

import re
from utils.deadline import deadline
from utils.code_features import get_indent_levels
from utils.line_features import get_indent, is_whitespace_line, is_comment
## 
## FEATURES
##

class Feature:
  def add_to_annotations(self, line_no, error, annotations):
    if line_no not in annotations:
      annotations[line_no] = []
    annotations[line_no].append(error)

@deadline(1)
class FeatureIndentation(Feature):
  """Finds misindended lines"""

  def __repr__(self):
    return "Indentation"

  def compute(self, code, annotations):

    indentations = {} #how far indented levels should be

    lines = code.lines
    levels = get_indent_levels(lines)
    # find the distribution of indentations for each indent level
    for line_no, line in enumerate(lines):

      _levels = levels[line_no]
      if _levels == None: # lines ignored because they are comments
        continue

      indent = get_indent(line) 
      for level in _levels:
        if level not in indentations:
          indentations[level] = [indent]
        else:
          indentations[level].append(indent)
      
    # find the most common indentations for each indent level
    # ensuring that each successive level is deeper
    try:
      common_indentation = {}
      for level, indents in indentations.iteritems():
        s = set(indents)
        if level == 0:
          common_indentation[level] = max(s, key=indents.count)
        else: 
          last_indentation = common_indentation[level-1]
          most_common = max(s, key=indents.count)
          # if indent is not deeper
          if most_common <= last_indentation:

            # TODO(fil): pass error when indent is not deeper
            while most_common <= last_indentation:
              s -= set([most_common])
              if len(s) == 0:
                most_common = max(set(indents), key=indents.count)
                break
              most_common = max(s, key=indents.count)

          common_indentation[level] = most_common
    except KeyError as e:
      print "Parsing error in feature_indentation (%s)" % e

    # find which lines don't match the expected indentation
    for line_no, line in enumerate(lines):
      _levels = levels[line_no]
      if _levels == None:
        continue

      expected_indents = []
      for level in _levels:
        try:
          expected_indents.append(common_indentation[level])
        except KeyError:
          continue

      indent = get_indent(line) 
      if expected_indents and indent not in expected_indents:

        error = "expected indent %i, got %i" % (expected_indents[0], indent)
        self.add_to_annotations(line_no, error, annotations)

@deadline(1)
class FeatureLineLength(Feature):
  """Finds lines that are too long"""

  def __repr__(self):
    return "Line length"

  def compute(self, code, annotations):
    for line_no, line in enumerate(code.lines):
      if len(line.rstrip()) > LINE_LENGTH_THRESHOLD:
        error = "line is too long"
        self.add_to_annotations(line_no, error, annotations)


@deadline(1)
class FeatureInconsistentBrackets(Feature):
  """Whether bracket is consistent after params"""

  def __repr__(self):
    return "Consistent bracket placement"

  def compute(self, code, annotations):
    iterator = re.finditer(r"(\)\s*?{)", code.text)
    occurences = []

    for occurence in iterator:
      occurences.append(occurence)

    if not occurences:
      return

    # process occurences to remove whitespace after first newline, find most common
    processed_occurences = map(lambda x: re.sub(r"\)[\ \t\r\f]*?\n", ")\n",
                                          re.sub(r"\n[\ \t\r\f]*", "\n", x.group())), occurences)

    most_common = max(set(processed_occurences), key=processed_occurences.count)

    # annotate the cases that don't conform to the common
    errors = []
    for index, occurence in enumerate(occurences):
      if processed_occurences[index] != most_common:

        # allow exception if it's flush left. some people start code blocks with a { on the next line
        # when all other code is ) { style
        # if flush left is not appropriate, the indent checker will catch it instead
        match = occurences[index].group()
        if match.count("\n{") == 1:
          continue

        # look up the corresponding line to the occurence
        span = occurence.span()
        start, end = code.get_lines_for_span(span)
        error = "inconsistent bracket placement"
        self.add_to_annotations(end, error, annotations) 
    return occurences 


@deadline(1)
class FeatureExcessiveWhitespace(Feature):
  """Finds places where there is a large amount of unnecessary whitespace"""

  def __repr__(self):
    return "Excessive whitespace"

  def compute(self, code, annotations):
    start_line = 0
    whitespace_run = 0
    for line_no, line in enumerate(code.lines):
      if is_whitespace_line(line):
        if whitespace_run > 0:
          whitespace_run += 1 
        else:
          whitespace_run = 1
          start_line = line_no
      else:
        # end of run
        if whitespace_run > MAX_WHITESPACE_LINES:
          error = "Excess whitespace"
          self.add_to_annotations(start_line, error, annotations)
        whitespace_run = 0


@deadline(1)
class FeatureInlineComments(Feature):
  """Finds places where inline comments don't conform"""

  def __repr__(self):
    return "Poorly formatted inline comment"

  def compute(self, code, annotations):
    for line_no, line in enumerate(code.lines):
      _line = line.strip()
      if _line.startswith("//"):
        if _line[2:3] != " ":
          error = "Need single space after // for inline comment"
          self.add_to_annotations(line_no, error, annotations)


@deadline(1)
class FeatureCommentAtTop(Feature):
  """Finds files that are missing a comment at the top"""

  def __repr__(self):
    return "Comment missing at top of file"

  def compute(self, code, annotations):
    for line_no, line in enumerate(code.lines):
      _line = line.strip()
      if not _line:
        continue
      if not is_comment(_line):
        error = "Each file should have a comment at the top"
        self.add_to_annotations(0, error, annotations)
      return


@deadline(1)
class FeatureSpaceAfterKeyword(Feature):
  """Finds keywords that don't have a space after them"""

  def __repr__(self):
    return "Keyword missing a space after"

  keywords = ["if", "for", "while"]

  def compute(self, code, annotations):
    for line_no, line in enumerate(code.stripped):
      for keyword in keywords:
        if re.match(r"\b%s\(" % keyword, bad):
          error = "The keyword %s should have a space after, to not confuse with a function" % keyword
          self.add_to_annotations(line_no, error, annotations)


@deadline(1)
class FeatureNotEnoughWhitespace(Feature):
  """Finds places where there are runs of unindented, unbroken code"""

  #TODO(fil): don't penalize for top level, just level > 0

  def __repr__(self):
    return "Not enough whitespace"

  def compute(self, code, annotations):
    start_line = 0
    no_whitespace_run = 0
    levels = None

    for line_no, line in enumerate(code.lines):

      level = code.levels[line_no] 
      if no_whitespace_run > 0:
        if not code.levels[line_no]:
          if no_whitespace_run > MAX_NON_WHITESPACE_LINES:
            error = "Not enough whitespace"
            self.add_to_annotations(start_line, error, annotations)
          no_whitespace_run = 0
          continue

        levels = levels & set(level) # check for consistent indent
        if len(levels) == 0 or is_whitespace_line(line):
          if no_whitespace_run > MAX_NON_WHITESPACE_LINES:
            error = "Not enough whitespace"
            self.add_to_annotations(start_line, error, annotations)
          no_whitespace_run = 0
        else:
          if 0 not in code.levels[line_no]:
            no_whitespace_run += 1
          
      elif not is_whitespace_line(line) and not is_comment(line) and level:
        levels = set(level)
        no_whitespace_run = 1
        start_line = line_no

@deadline(1)
class FeatureInconsistentParamSpacing:
  """Finds whether spacing within parameters is consistent"""

  def __repr__(self):
    return "Consistent parameter spacing"

  def compute(self, code, annotations):
    pass

@deadline(1)
class FeatureMultipleStatementsPerLine:
  """Whether there are multiple statements per line"""

  def __repr__(self):
    return "Multiple statements per line"

  def compute(self, code, annotations):
    pass

# the features to run
production_feature_list = [FeatureIndentation,
                FeatureLineLength,
                FeatureInconsistentBrackets,
                FeatureExcessiveWhitespace,
                FeatureInlineComments,
                FeatureCommentAtTop]

test_feature_list = [
                FeatureSpaceAfterKeyword
                ]
#                FeatureNotEnoughWhitespace]
