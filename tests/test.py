import os
import unittest
import zipfile
from functools import partial
from tempfile import TemporaryDirectory
from coconerd.main import code_statistics, download_github, process_path, \
  code_attrs
from hashlib import md5
import base64
from multiprocessing import Queue

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

  def test_download_github_commit(self):
    with TemporaryDirectory(suffix='_coconerd') as fd:
      md5_checksum = r'2b524be404273970cc72ac98eb294b16'
      url = b'aHR0cHM6Ly9naXRodWIuY29tL3RydW5nbnQxMy9iaWdhcnJheS9hcmNoaXZ' \
            b'lLzRjOWJjZGQ0OGRh\nNDk1Y2IxZjkxOTczMGRjNTIxNjVjNWQzYzg3MDMuemlw\n'
      url = str(base64.decodebytes(url), 'utf-8')
      path = download_github(url=url, cache_dir=fd)
      with open(path, 'rb') as f:
        md5_hash = md5()
        for buf in iter(partial(f.read, 1024), b''):
          md5_hash.update(buf)
        self.assertEqual(md5_checksum, md5_checksum,
                         'Failed downloading from Github commit hash')

  def test_download_github_head(self):
    with TemporaryDirectory(suffix='_coconerd') as fd:
      url = b'aHR0cHM6Ly9naXRodWIuY29tL3RydW5nbnQxMy9iaWdhcnJheQ==\n'
      url = str(base64.decodebytes(url), 'utf-8')
      zip_path = download_github(url=url, cache_dir=fd)
      with zipfile.ZipFile(zip_path, 'r') as f:
        namelist = {os.path.basename(i) for i in f.namelist()}
        self.assertTrue(all(name in namelist for name in [
          'mmap_array.py',
          'setup.py',
          'test_mmaparray.py',
          'test_pointerarray.py'
        ]), 'Failed downloading from Github HEAD')

      queue = Queue()
      process_path(zip_path, queue)
      objs = [queue.get() for _ in range(queue.qsize())]
      self.assertTrue(all(i is None for i in objs[:-1]),
                      'process_path logic wrong.')
      attrs = dict(objs[-1][-1])
      self.assertTrue(all(k in attrs for k in code_attrs.keys()),
                      'missing attributes for code statistics.')
      queue.close()


if __name__ == '__main__':
  unittest.main()
