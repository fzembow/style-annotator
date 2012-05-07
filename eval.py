
import json, os, csv
from annotator import Code, annotate

PSET_1_SPEC = """
{
  "base_dir": "/home/fzembow/psets/2011/pset1",
  "files": ["chart.c", "greedy.c", "pennies.c"]
}
"""
PSET_6_SPEC = """
{
  "base_dir": "/home/fzembow/psets/2011/pset6",
  "files": ["speller.c"]
}
"""


GRADES_CSV = "/home/fzembow/grades.csv"
STATS = {
  0:[],
  1:[],
  2:[],
  3:[]
}


def main():
  grades = load_grades(GRADES_CSV, "pset1")
  eval_pset(PSET_1_SPEC, grades)
  get_aggregate_stats(STATS)


def load_grades(csv_file, pset):
  reader = csv.reader(open(csv_file, "rbU"))
  grades = {}
  for row in reader:
    assignment_pset = row[0]
    grade = row[1]
    student = row[3]

    if pset == assignment_pset:
      grades[str(student)] = grade
  return grades


def eval_pset(spec, grades):
  spec = json.loads(PSET_1_SPEC)
  base_dir = spec["base_dir"]
  pset_files = spec["files"]

  for student in os.listdir(base_dir):
    user_dir = os.path.join(base_dir, student)

    for pset_file in pset_files:
      pset_file_loc = os.path.join(user_dir, pset_file)

      try:
        code = Code(filename=pset_file_loc)
        annotations = annotate(code)
        num_errors = len(annotations)
        try:
          grade = grades[student]
          try:
            STATS[int(grade)].append(num_errors)
          except ValueError:
            # grade is "NULL" or not a number
            pass

        except KeyError:
          # student doesn't have this grade
          pass

      except IOError:
        #missing assignment file
        pass


def get_aggregate_stats(stats):
  for grade, errors in stats.iteritems():
    try:
      print grade, 1.0 * sum(errors) / len(errors)
    except ZeroDivisionError:
      # no assignments with this score
      pass

if __name__ == "__main__":
  main()
