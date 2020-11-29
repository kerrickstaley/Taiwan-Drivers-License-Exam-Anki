#!/usr/bin/env python3

import argparse
import genanki
import html
import os
import re
import sys
import textwrap
import yaml

from question import Question

parser = argparse.ArgumentParser(description='Convert YAML file containing questions into an Anki deck')
parser.add_argument('--input-yaml', required=True, help='Path to YAML file to load questions from')
parser.add_argument('--input-image-dir', help='Directory containing images')
parser.add_argument('--output-apkg', required=True, help='Path to write Anki package file to')


MODEL = genanki.Model(
  1670705034,
  "Taiwan Driver's License",
  fields=[
    {'name': 'Question'},
    {'name': 'Question Image'},
    {'name': 'Answer'},
  ],
  templates=[
    {
      'name': 'Card 1',
      'qfmt': textwrap.dedent('''\
          {{#Question Image}}
            {{Question Image}}
            <br>
          {{/Question Image}}
          {{Question}}
          '''.rstrip()),
      'afmt': textwrap.dedent('''\
          <span class="reveal-answer-{{Answer}}">
            {{FrontSide}}
            <span class='answer-O'>
              <hr id=answer>
              <div style="font-weight: bold">O (True)</div>
            </span>
            <span class='answer-X'>
              <hr id=answer>
              <div style="font-weight: bold">X (False)</div>
            </span>
          </span>
          '''.rstrip()),
    },
  ],
  css=textwrap.dedent('''\
      .card {
        font-family: arial;
        font-size: 20px;
        text-align: center;
        color: black;
        background-color: white;
      }

      .reveal-answer-1 .answer-1, .reveal-answer-2 .answer-2, .reveal-answer-3 .answer-3 {
        font-weight: bold;
        color: blue;
      }

      .nightMode .reveal-answer-1 .answer-1, .nightMode .reveal-answer-2 .answer-2, .nightMode .reveal-answer-3 .answer-3 {
        color: lightblue;
      }

      .answer-O, .answer-X {
        display: none;
      }

      .reveal-answer-O .answer-O, .reveal-answer-X .answer-X {
        display: block;
      }
      '''.rstrip()),
)


def question_to_note(question: Question) -> genanki.Note:
  if question.answer in {'1', '2', '3'}:
    pieces = re.split(r'\([1-3]\)', html.escape(question.question))

    if len(pieces) != 4:
      raise ValueError(f'Could not parse multiple choice question {repr(question.question)}')

    for choice in [1, 2, 3]:
      pieces[choice] = f'<span class="answer-{choice}">({choice})' + pieces[choice] + '</span>'

    if not pieces[0].strip():
      pieces = pieces[1:]

    question_text = '<br>'.join(pieces)
  else:
    question_text = question.question

  if question.question_image:
    image_text = f'<img src="{question.question_image}">'
  else:
    image_text = ''

  return genanki.Note(
    model=MODEL,
    fields=[question_text, image_text, question.answer],
    tags=[question.difficulty])


def main(args):
  questions = Question.load_list_from_yaml(args.input_yaml)

  deck = genanki.Deck(
    1395868281,
    "Taiwan Driver's License Written Test")

  media_files = []

  for question in questions:
    deck.add_note(question_to_note(question))

    if question.question_image:
      media_files.append(os.path.join(args.input_image_dir, question.question_image))

  package = genanki.Package(deck)
  package.media_files = media_files
  package.write_to_file(args.output_apkg)


if __name__ == '__main__' and not hasattr(sys, 'ps1'):
  main(parser.parse_args())
