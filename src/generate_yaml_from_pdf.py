#!/usr/bin/env python3

# Note: Some of this code was copied/modified from https://github.com/robhawkins/drive-taiwan. Please excuse any
# inconsistencies in style :)

import argparse
import glob
import hashlib
import os
import re
import shutil
import subprocess
import sys
import tempfile
from typing import List

from question import Question

import bs4
from natsort import natsorted

parser = argparse.ArgumentParser(description='Convert a PDF file from thb.gov.tw into a .yaml file containing a machine-readable version of the data')
parser.add_argument('--input-pdf', required=True, help='Path to PDF file to extract')
parser.add_argument('--existing-yaml', help='Optional path to existing YAML file to copy difficulty ratings from')
parser.add_argument('--output-yaml', required=True, help='Path to write output YAML file to')
parser.add_argument('--output-image-dir', help='Optional path to write output images to')


## QuestionFile is used to build up an object and export to CSV.
class QuestionFile(object):
  FILEMAP = {
              '機車法規是非題-中文' : ('moto', 'rules', 'true','chinese'),
              '機車法規選擇題-中文' : ('moto', 'rules', 'choice', 'chinese'),
              '機車標誌是非題-中文' : ('moto', 'signs', 'true','chinese'),
              '機車標誌選擇題-中文' : ('moto', 'signs', 'choice','chinese'),
              '汽車標誌是非題-中文' : ('car', 'signs', 'true', 'chinese'),
              '汽車標誌選擇題-中文' : ('car', 'signs', 'choice', 'chinese'),
              '汽車法規是非題-中文' : ('car', 'rules', 'true', 'chinese'),
              '汽車法規選擇題-中文' : ('car', 'rules', 'choice', 'chinese'),
              '機車法規是非題-英文1090116' : ('moto', 'rules', 'true', 'english'),
              '機車法規選擇題-英文1090116' : ('moto', 'rules', 'choice', 'english'),
              'Signs-True or False／English〈機車標誌是非題-英文〉' : ('moto', 'signs', 'true', 'english'),
              'Signs-Choice／English〈機車標誌選擇題-英文〉' : ('moto', 'signs', 'choice', 'english'),
              '汽車法規選擇題-英文1090116' : ('car', 'rules', 'choice', 'english'),
              '汽車法規是非題-英文1090116' : ('car', 'rules', 'true', 'english'),
              'Signs-Choice／English(汽車標誌選擇題-英文)' : ('car', 'signs', 'choice', 'english'),
              'Signs-True or False／English(汽車標誌是非題-英文)' : ('car', 'signs', 'true', 'english'),
            }

  for k in list(FILEMAP):
    v = FILEMAP[k]
    id=v[3]+'-'+v[0]+'-'+v[1]+'-'+v[2]
    FILEMAP[id] = v

  def __init__(self,filebase='',language='',vehicle='',signsrules='',truechoice='',questions=(),images=(),ankiexport=''):
    self.filebase = filebase
    self.language = language
    self.vehicle = vehicle
    self.signsrules = signsrules
    self.truechoice = truechoice
    self.questions = list(questions)
    self.images = list(images)
    self.ankiexport = ankiexport

    attributes_set = (language and vehicle and signsrules and truechoice)
    if attributes_set:
      pass
    elif filebase in self.FILEMAP:
      (self.vehicle, self.signsrules, self.truechoice, self.language) = self.FILEMAP[filebase]
    else:
      raise RuntimeError(f'Unknown filebase {repr(filebase)}')

    if ankiexport:
      self.readLabels()

  def readLabels(self):
    self.labels = {}
    with open(self.ankiexport) as f:
      reader = csv.reader(f, delimiter='\t')
      for line in reader:
        id = line[0]
        tag = line[-1]
        self.labels[id] = tag

  def getFileID(self):
    return self.language+'-'+self.vehicle+'-'+self.signsrules+'-'+self.truechoice
  def newQuestion(self):
    q = Question()
    self.questions.append(q)
    return q
  def getQuestion(self,i):
    return self.questions[i]
  def prettyAll(self):
    self.finished()
    return '\n'.join(q.pretty() for q in self.questions)+'\n'
  def writeCSV(self, dir):
    file = dir + '/' + self.getFileID() + '.csv'
    f = open(file, 'w')
    f.write(self.prettyAll())
    f.close()
    print("Wrote file: "+file)
  def finished(self):
    lastq = self.questions[-1]
    if not lastq:
      del self.questions[-1]
    if self.signsrules == 'signs':
      self.populateImageNames()
      for i,q in enumerate(self.questions):
        q.question = '<img src="'+self.images[i]+'"/><br/>'+q.question
    self.finished_called = 1
  def copyImages(self, work, anki):
    if not self.finished_called:
      self.finished()
    images = [f for f in glob.glob(work + '/' + self.filebase + '*.*') if not re.match('.*\.xml', f)]
    for i,f in enumerate(natsorted(images)):
      copy2(f, anki + '/' + self.images[i])
  def populateImageNames(self):
    self.images = []
    newbase = self.getFileID()
    for i,q in enumerate(self.questions):
      qnum = i+1
      imagefile = newbase+'-'+str(qnum)+'.png'
      self.images.append(imagefile)


def parse_pdf(path_to_pdf: str, has_images: bool = False) -> QuestionFile:
  filename = os.path.splitext(os.path.basename(path_to_pdf))
  base = filename[0]

  qfile = QuestionFile(filebase=base)

  tempdir = tempfile.mkdtemp()

  workingDir = tempdir + '/' + qfile.getFileID()
  mkdir_p(workingDir)

  outputFile = os.path.join(tempdir, qfile.getFileID()+'.csv')

  xmlfile = workingDir + '/' + base + '.xml'

  subprocess.check_call(
    ['pdftohtml', '-xml', path_to_pdf, xmlfile],
    stdout=subprocess.DEVNULL)

  filehandler = open(xmlfile)

  soup = bs4.BeautifulSoup(filehandler,'lxml')

  current_q = qfile.newQuestion()

  state = ''
  qnum = 0

  ignorable_lines = [ '^題號$',
                      '^答案$',
                      '^題目圖示$',
                      '^題\s*目$',
                      '^第\d+頁/共\d+頁$',
                      '^機車標誌、標線、號誌..題$',
                      '^分類$',
                      '^編號$',
                      '^機車法規選擇題$',
                      '^機車法規是非題$',
                      '^汽車法規選擇題$',
                      '^【英文】$',
                      '^汽車法規是非題$',
                      '^汽車標誌、標線、號誌.含汽車儀表警示、指示燈...題$',
                      '^分類編號$',
                      '^分類編$',
                      '^號$',
                      '^題號答案$',
                    ]


  for page in soup.findAll('page'):
    pageheight = int(page['height'])
    pagewidth = int(page['width'])
    for text in page.findAll('text'):
      top_pos = float(text['top']) / pageheight
      left_pos = float(text['left']) / pagewidth
      txt = text.get_text()
      txt_strip = txt.strip()
      txt_nospace = re.sub('\s+','',txt)
      if not txt_strip:
        continue
      skip = False
      for ignore in ignorable_lines:
        if re.match(ignore, txt_nospace):
          skip = True
          continue
      if skip:
        continue
      if re.match('^[0-9]{3}$',txt_strip):
        state = 'found_qnum'
        qnum = int(txt_strip)
        qnum_i = qnum-1
        if current_q:
          current_q.question = re.sub('\n','',current_q.question)
          current_q = qfile.newQuestion()
        current_q.number = qnum
        continue
      elif state == 'found_qnum':
        if re.match('^[0-9OX]$',txt_strip) or txt_strip == 'Ｘ' or txt_strip == 'Ｏ':
          state = 'found_ans'
          if current_q.answer != '':
            warning("%d: Answer being overwritten" % (qnum))
          if txt_strip == 'Ｏ': txt_strip = 'O'
          elif txt_strip == 'Ｘ': txt_strip = 'X'
          current_q.answer = txt_strip
        else:
          warning("%d: Answer not found after question number" % (qnum))
      elif state == 'found_ans' and not re.match('^[0-9]+$',txt_strip):
        current_q.question += txt
      elif re.match('^[0-9]{1,2}$',txt_strip) and left_pos > 0.75:
        current_q.category = txt_strip
  filehandler.close()

  for quest in qfile.questions:
    quest.question = normalize_question_text(quest.question)

    # Fix a specific malformed question.
    quest.question = quest.question.replace('¬#¦', '(3) ')

  if has_images:
    image_paths = glob.glob(os.path.join(workingDir, '*.png'))

    if len(qfile.questions) != len(image_paths):
      raise RuntimeError(
        f'Different number of questions and images: {len(qfile.questions)} questions and {len(image_paths)} images')

    for quest, image_path in zip(qfile.questions, natsorted(image_paths)):
      quest.question_image = image_path

  return qfile


def copy_difficulty_values_from_existing_yaml(dst: QuestionFile, src: List[Question]):
  dd = DifficultyDict()
  for quest in src:
    dd[quest] = quest.difficulty

  for quest in dst.questions:
    quest.difficulty = dd.get(quest)


def normalize_question_text(question: str):
  question = re.sub(r'\( *([123]) *\)',r' (\1) ', question)
  question = question.replace('<br/>', ' ')
  question = re.sub(' +', ' ', question)
  question = question.strip()
  return question


class DifficultyDict:
  """
  Maps from `question` instances to their associated difficulty.

  The difficulty value may be "easy", "medium", "hard", or "impossible".

  TODO I think we can just get rid of this and use a regular dict.
  """
  def __init__(self):
    self._dict = {}

  @classmethod
  def _key(cls, question: Question) -> str:
    return f'{normalize_question_text(question.question)}|{question.question_image}|{question.answer}'

  def __setitem__(self, question: Question, difficulty: str) -> None:
    self._dict[self._key(question)] = difficulty

  def __getitem__(self, question: Question) -> str:
    return self._dict[self._key(question)]

  def get(self, question: Question) -> str:
    return self._dict.get(self._key(question), Question.UNKNOWN_DIFFICULTY)

  def __repr__(self):
    return self._dict.__repr__()


def warning(*objs):
  print("WARNING: ", *objs, file=sys.stderr)

def mkdir_p(path):
  try:
    os.makedirs(path)
  except OSError as exc: # Python >2.5
    if exc.errno == errno.EEXIST and os.path.isdir(path):
      pass
    else: raise


def sha256_file(path: str) -> str:
  # This is only suitable for small files because it reads the entire file into memory.
  sha256 = hashlib.sha256()
  with open(path, 'rb') as f:
    sha256.update(f.read())

  return sha256.hexdigest()


def copy_images_to_output_dir_and_update_paths(questions, output_image_dir):
  """
  Copy images into images/ directory and update question.question_image for each question in `questions`.


  In the input to this function, question.question_image is an absolute path to the png image. This function copies
  that png image into the images/ directory and changes question.question_image to the filename in images/ (it
  modifies the input Question objects).

  For example, in the input, questions[0].question_image might be the string

      '/tmp/tmp0knp4k5i/english-moto-signs-choice/Signs-Choice／English〈機車標誌選擇題-英文〉-1_1.png'

  This function will copy that image to images/6f53d394460c8214.png and change questions[0].question_image to

      '6f53d394460c8214.png'
  """
  for quest in questions:
    if quest.question_image is None:
      continue

    dest_fname = f'{sha256_file(quest.question_image)[:16]}.png'
    dest_path = os.path.join(output_image_dir, dest_fname)
    shutil.copy(quest.question_image, dest_path)
    quest.question_image = dest_fname


def main(args):
  qfile = parse_pdf(args.input_pdf, has_images=bool(args.output_image_dir))

  if args.output_image_dir:
    copy_images_to_output_dir_and_update_paths(qfile.questions, args.output_image_dir)

  if args.existing_yaml:
    copy_difficulty_values_from_existing_yaml(qfile, Question.load_list_from_yaml(args.existing_yaml))

  Question.dump_list_to_yaml(qfile.questions, args.output_yaml)


if __name__ == '__main__' and not hasattr(sys, 'ps1'):
  main(parser.parse_args())
