import signal

class TimedOutExc(Exception):
  pass

def deadline(timeout, *args):
  """A decorator that creates a max execution time for a function"""
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


