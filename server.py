#!/usr/bin/python

"""Renders assignments annotated with style features"""

__author__ = "Fil Zembowicz (fil@filosophy.org)"

from annotator import annotate, get_text, Code
from mako.template import Template
from mako.runtime import Context
from StringIO import StringIO
import sys
from flask import Flask, request

app = Flask(__name__)

@app.route("/")
def main():
  
  template = Template(filename="templates/index.txt")
  return template.render()

@app.route("/annotate", methods=["POST"])
def process():
  if "code" in request.form and request.form["code"]:
    code_input = request.form["code"]
    code = Code(text=code_input)
    annotations = annotate(code)
    
    template = Template(filename="templates/annotated.txt",
                        default_filters=['decode.utf8'],
                        input_encoding='utf-8',
                        output_encoding='utf8')
    return template.render(lines=code.lines, annotations=annotations)
  else:
    return "make sure you pasted code"    

def main():
  if len(sys.argv) > 1 and sys.argv[1] == "debug":
    app.run(debug=True)
  else:
   app.run(debug=False)

if __name__ == "__main__":
  main()
