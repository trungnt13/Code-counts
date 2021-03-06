import shutil
import sys
import zipfile
from collections import defaultdict
from pathlib import Path
from typing import Tuple, List, Dict, Optional

import os
import re
from urllib.request import urlretrieve, urlopen
from urllib.error import HTTPError
from tqdm import tqdm
from multiprocessing import Queue, Process
from argparse import ArgumentParser, Namespace

github_pattern = re.compile(r'(http(s)?:\/{2})?(www\.)?github\.com\/.*\/.*\/?')

code_attrs = dict(
  for_loop=re.compile(r'for\s+.*:*'),
  while_loop=re.compile(r'while\s+.*:*'),
  if_cond=re.compile(r'if\s+.*:*'),
  func_def=re.compile(r'def\s[\w\_][\w\_\d]*\('),
  class_def=re.compile(r'class\s[\w\_][\w\_\d]*\({0,1}'),
  lines=re.compile(r'.+\n')
)


# ===========================================================================
# Helpers
# ===========================================================================
def download_github(url: str, cache_dir: str) -> Path:
  if url[-1] == '/':
    url = url[:-1]
  org_url = url
  repo_name = url.split('/')[-1]
  user_name = url.split('/')[-2]
  if '.zip' not in os.path.splitext(str(url)):
    url = f'{url}/archive/refs/heads/main.zip'
    cache_path = os.path.join(cache_dir, f'{user_name}_{repo_name}.zip')
  else:  # somehow download using commit hash has .zip already
    cache_path = os.path.join(cache_dir, f'{user_name}_{repo_name}')
  if not os.path.exists(cache_path):
    try:
      conn = urlopen(url)
      conn.close()
    except HTTPError:
      url = f'{org_url}/archive/refs/heads/master.zip'
    prog = tqdm(desc=f'Downloading {user_name}/{repo_name}', unit="Kb")

    def report_hook(block_number, read_size, total_file_size):
      prog.update(read_size / 1024.)

    urlretrieve(url, cache_path, report_hook)
    prog.close()
  return Path(cache_path)


def code_statistics(code: str) -> List[Tuple[str, int]]:
  return [(key, len(attr.findall(code))) for key, attr in code_attrs.items()]


def process_path(path: Path, queue: Queue):
  stats = defaultdict(int)
  if path.is_dir():
    for py_file in path.rglob(r'*.py'):
      with open(py_file, 'r') as f:
        for k, v in code_statistics(f.read()):
          stats[k] += v
        queue.put(None)
  elif '.zip' in str(path).lower():
    with zipfile.ZipFile(path, mode='r') as f:
      for py_file in filter(lambda name: os.path.splitext(name)[-1] == '.py',
                            f.namelist()):
        for k, v in code_statistics(str(f.read(py_file), 'utf-8')):
          stats[k] += v
        queue.put(None)
  elif '.py' in str(path).lower():
    with open(path, 'r') as f:
      for k, v in code_statistics(f.read()):
        stats[k] += v
      queue.put(None)
  queue.put((path, stats))


def get_arguments(args: Optional[List[str]] = None) -> Namespace:
  parser = ArgumentParser()
  parser.add_argument('path_or_url',
                      help='path to local directory or url to github repo, '
                           'multiple input concatenated by ,')
  parser.add_argument('-cache',
                      help='path to cache directory',
                      default='/tmp/code_counts')
  parser.add_argument('--clear',
                      help='clear all cached source code',
                      action='store_true')
  parsed_args = parser.parse_args(args)
  if parsed_args.path_or_url == 'default':
    parsed_args.path_or_url = 'https://github.com/trungnt13/odin-ai,' \
                              'https://github.com/trungnt13/sisua,' \
                              'https://github.com/trungnt13/bigarray,' \
                              'https://github.com/trungnt13/odin_old'
  parsed_args.path_or_url = parsed_args.path_or_url.split(',')
  if parsed_args.clear and os.path.exists(parsed_args.cache):
    print('Remove cache folder at:', parsed_args.cache)
    shutil.rmtree(parsed_args.cache)
  return parsed_args


def validate_path(paths: List[str], cache_path: str) -> Tuple[
  List[str], Dict[str, str]]:
  all_path = []
  trace = dict()
  for p in paths:
    org_path = p
    if os.path.exists(os.path.expanduser(p)):
      p = Path(p).expanduser()
    elif github_pattern.match(p):
      p = download_github(p, cache_path)
    else:
      raise ValueError(
        f'Only support native path or github link, but given {p}')
    all_path.append(p)
    trace[p] = org_path
  return all_path, trace


def show_stats(stats: Dict[str, Dict[str, int]], trace: Dict[str, str]):
  total = defaultdict(int)
  for k, v in stats.items():
    print(trace[k])
    for i, j in v.items():
      print(f' {i:10s}: {j}')
      total[i] += j

  print('---Total:')
  for i, j in total.items():
    print(f' {i:10s}: {j}')
    total[i] += j


# ===========================================================================
# Main
# ===========================================================================
def main(paths: List[str], cache_path: str = '/tmp/code_counts'):
  if not os.path.exists(cache_path):
    os.makedirs(cache_path)

  all_path, trace = validate_path(paths, cache_path)

  queue = Queue()
  n_jobs = len(all_path)
  prog = tqdm(desc='Processing', unit='files')
  processes = list(map(
    lambda path: Process(target=process_path, args=(path, queue)),
    all_path))
  for p in processes:
    p.start()
  stats = dict()
  while n_jobs > 0:
    n = queue.get()
    if n is None:
      prog.update(1)
    else:
      stats[n[0]] = n[1]
      n_jobs -= 1
  for p in processes:
    p.join()
  queue.close()
  prog.close()

  show_stats(stats, trace)


if __name__ == '__main__':
  args = get_arguments()
  main(args.path_or_url, args.cache)
