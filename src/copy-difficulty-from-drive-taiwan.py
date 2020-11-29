#!/usr/bin/env python3
# Copy difficulty ratings from https://github.com/robhawkins/drive-taiwan
# Note: This only works for the "signs" PDFs, because those haven't been updated in the time since drive-taiwan was
# published.

import argparse
import os
import sys
import yaml

parser = argparse.ArgumentParser()
parser.add_argument('--input', required=True, help='Path to "All Decks.txt" file')
parser.add_argument('--yamls', required=True, nargs='+', help='YAML files to update')


def main(args):
  question_id_to_difficulty = {}
  with open(args.input) as f:
    for line in f:
      line = line.rstrip('\n')
      question_id = line.split('\t')[0]
      difficulty = line.split('\t')[-1] or 'unknown_difficulty'
      question_id_to_difficulty[question_id] = difficulty

  for yaml_file in args.yamls:
    with open(yaml_file) as f:
      data = yaml.safe_load(f)
    
    for entry in data:
      if entry['difficulty'] != 'unknown_difficulty':
        continue

      question_id = f"{os.path.basename(yaml_file)[:-len('.yaml')]}-{entry['number']:03}"

      if question_id not in question_id_to_difficulty:
        raise RuntimeError(f'Did not find question_id {question_id} in All Decks.txt')
      
      entry['difficulty'] = question_id_to_difficulty[question_id]
    
    with open(yaml_file, 'w') as f:
      yaml.dump(data, f, sort_keys=False)


if __name__ == '__main__' and not hasattr(sys, 'ps1'):
  try:
    main(parser.parse_args())
  except:
    import pdb; pdb.post_mortem()
