import re
from line_features import is_whitespace_line, is_comment, strip, is_paren, is_incomplete_statement

KEYWORDS = ["for", "if", "else", "while"];

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


