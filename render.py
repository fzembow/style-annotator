#!/usr/bin/python

"""Renders assignments annotated with style features"""

__author__ = "Fil Zembowicz (fil@filosophy.org)"

from utils import annotate, get_text, Code
from mako.template import Template
from mako.runtime import Context
from StringIO import StringIO
import sys

def main(): 
  if len(sys.argv) < 2:
    print "you need to provide a file to annotate"
    sys.exit(1)

  filename = sys.argv[1] 
  print render(filename)

def render(filename):
  code = Code(filename)
  annotations = annotate(code)

  template = Template(filename="templates/assignment.txt")
  buf = StringIO()
  ctx = Context(buf, lines=code.lines, annotations=annotations)
  template.render_context(ctx)
  return buf.getvalue()

if __name__ == "__main__":
  main()

