from copy import deepcopy
import functools
import inspect
import yaml

from typing import List


class Question(object):
  UNKNOWN_DIFFICULTY = 'unknown_difficulty'

  def __init__(self, question='', question_image=None, answer='', number='', category='', difficulty=UNKNOWN_DIFFICULTY, note=''):
    self.question = question
    self.question_image = question_image
    self.answer = answer
    self.number = number
    self.category = category
    self.difficulty = difficulty
    self.note = note

  def __repr__(self):
    attrs = ['question', 'question_image', 'answer', 'number', 'category', 'difficulty', 'note']
    pieces = []
    for attr in attrs:
      pieces.append('{}={}'.format(attr, repr(getattr(self, attr))))
    return '{}({})'.format(self.__class__.__name__, ', '.join(pieces))

  def __eq__(self, other):
    return self.__class__ is other.__class__ and self.__dict__ == other.__dict__

  def __ne__(self, other):
    return not (self == other)

  def __bool__(self):
    empty = Question()
    return self != empty

  def to_dict(self):
    ret = dict(self.__dict__)

    for key in list(ret):
      if not ret[key]:
        del ret[key]

    return ret

  @classmethod
  def load_list_from_yaml(cls, path_to_yaml: str) -> List['Question']:
    with open(path_to_yaml) as f:
      data = yaml.safe_load(f)

    ret = []
    for entry in data:
      ret.append(cls(
        question=entry.get('question', ''),
        question_image=entry.get('question_image'),
        answer=str(entry.get('answer', '')),
        number=entry.get('number', ''),
        category=str(entry.get('category', '')),
        difficulty=entry.get('difficulty', cls.UNKNOWN_DIFFICULTY),
        note=entry.get('note', ''),
      ))

    return ret

  @classmethod
  def dump_list_to_yaml(cls, qlist: List['Question'], path_to_yaml: str):
    data = []
    for entry in qlist:
      data.append(entry.to_dict())

    with open(path_to_yaml, 'w') as f:
      yaml.dump(data, f, sort_keys=False)
