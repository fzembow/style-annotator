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
KEYWORDS = ["for", "if", "else", "while"];

import signal, re, string
class TimedOutExc(Exception):
  pass

def deadline(timeout, *args):
  def decorate(f):
    def handler(signum, frame):
      raise TimedOutExc()

    def new_f(*args):
      
      try:
        signal.signal(signal.SIGALRM, handler)
        signal.alarm(timeout)
        return f(*args)
      except ValueError:
        return f(*args)

    new_f.__name__ = f.__name__
    return new_f
  return decorate

@deadline(1)
def get_indent_levels(lines):
  """Finds the allowed indentation levels
  
  The dictionary returned maps line number (0-indexed) 
  to the appropriate level of indentation of that line.
  'Level of indentation' is not the actual amount of whitespace,
  but rather just how many units indented the line should be.
  This allows for a more generic indentation validator in 
  feature_indentation() that is agnostic to number of tabs, etc.
  """
  levels = {}

  depth = 0
  statement_depth = 0     # for bracket-free shorthand

  # for switch statements
  case_adjust = 0         # indent applied to next row
  switch_parens = 0       # keep track of parens to see if switch is ended
  is_switch = False       # 
  was_break = False

  ignore = get_ignore_lines(lines) # find whitespace, comments

  for line_no, line in enumerate(lines):

    stripped = strip(line)

    # indentation due to parens
    num_close_parens = len(re.findall(r"}", stripped))
    num_open_parens = len(re.findall(r"{", stripped))
    if num_open_parens == num_close_parens:
      num_close_parens = num_open_parens = 0
    depth -= num_close_parens

    # indentation due to switch statements
    if is_switch:
      switch_parens += num_open_parens - num_close_parens

    if re.match("case.*:$", stripped) or re.match("default.*:$", stripped):
      if is_switch:
        depth -= 1
        case_adjust = 1
      else:
        is_switch = True
        case_adjust = 1 

    # end of switch statement
    if switch_parens < 0:
      is_switch = False
      switch_parens = 0
      depth -= 1

    # compute the actual indent level
    if ignore[line_no]:
      levels[line_no] = None
    else:
      new_depth = None
      if "{" in line:
        new_depth = depth
        statement_depth = 0
      else:
        new_depth = depth + statement_depth

      levels[line_no] = [new_depth]

      # allow for some uncertainty in some cases
      # comments in switch -- allow to be one less
      if is_switch and is_comment(line):
        levels[line_no] += [new_depth - 1]
      # parens by themselves -- allow to be indented one
      if is_paren(line):
        levels[line_no] += [new_depth + 1]
      # line starts with } and ends with {, asjust to be one lessj
      if stripped.startswith("}") and stripped.endswith("{"):
        levels[line_no].remove(new_depth)
        levels[line_no] += [new_depth - 1]
        
    # adjustments to next line below

    # open parens: next line should be indented
    depth += num_open_parens
    depth += case_adjust
    case_adjust = 0

    # look for bracked-free shorthand
    if is_incomplete_statement(stripped) and not "{" in stripped:
      for keyword in KEYWORDS:
        if stripped.startswith(keyword):
          statement_depth += 1
          break
    else:
      statement_depth = 0

  return levels
 
def get_ignore_lines(lines):
  """Finds the lines of code to ignore indent in"""
  ignore = {}
  multiline = False
  for line_no, line in enumerate(lines):
    # whitespace line
    if is_whitespace_line(line):
      ignore[line_no] = True 
    # new multiline comment
    elif re.match(r"\s*/\*", line):
      multiline = True
      ignore[line_no] = False # this line should be inline
    # continuing multiline comment
    elif multiline:
      ignore[line_no] = True
      if re.search(r"\*/", line):
        multiline = False
    # single line comment -- want these to be aligned
    elif re.match(r"\s*?//", line): 
      ignore[line_no] = False
    else:
      ignore[line_no] = False

  return ignore

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
      if indent not in expected_indents:

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
                FeatureExcessiveWhitespace]

test_feature_list = [
                FeatureNotEnoughWhitespace]
