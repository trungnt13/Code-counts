import unittest
from coconerd.main import code_statistics

source = \
  r"""
for i in range(10):
  for j in range(11):
    pass

[i for i in range(10) if i > 5]

if i == 5:
  pass

def test():
  pass

def test1(a):
  if a > 1:
    pass
  else:
    pass
    

class Test:
  pass

class Test1(object):
  pass
  """


class CodeCountTest(unittest.TestCase):

  def test_code_stats(self):
    stats = dict(code_statistics(source))
    true_values = dict(
      for_loop=3,
      while_loop=0,
      if_cond=3,
      func_def=2,
      class_def=2,
      lines=25
    )
    for k, v in true_values.items():
      self.assertEqual(v, stats[k],
                       f'[{k}] true value is {v} but return {stats[k]}')


if __name__ == '__main__':
  unittest.main()
