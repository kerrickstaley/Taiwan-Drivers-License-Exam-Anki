# Taiwan Driver's License Anki Deck

This repo contains code to generate an [Anki](https://apps.ankiweb.net/) flashcard deck which helps you study for the exams for Taiwan's scooter and car driver's licenses.

You can [download the deck from AnkiWeb](https://ankiweb.net/shared/info/2139136408).

It uses the [official question bank PDFs](https://www.thb.gov.tw/catalog?node=9ea3538d-e302-4c8c-a2f9-038ad2caf714).

This repo borrows heavily from [robhawkins's drive-taiwan project](https://github.com/robhawkins/drive-taiwan); thanks to Rob for his work on this!

## Goal

The goal of this project is to (1) identify the harder questions and (2) make studying them easier.

Some of the issues with the existing test and resources are,

  * There are now 1,600 questions for the car and scooter tests.  Before July 2015 there were only 600
  * Most questions are easy, but there are enough hard ones that it is easy to fail the test unless you review them
  * It is difficult to identify and focus on studying the hard questions
  * Study material consists of all possible questions rather than a more concise presentation of what you should know

## Requirements

This project should work on Linux, macOS, and Windows, but it has only been tested on Linux.
To use it, you need to install Python 3, the `pdftohtml` utility from Poppler, and the following Python 3 packages:
- `genanki`
- `natsort`
- `beautifulsoup4`
- `pyyaml`

## Usage

You can run the code with the command

    make

This will generate 8 `.apkg` files in the `apkgs/` directory, one for each of the question bank PDFs
(see the [pdfs dir](https://github.com/kerrickstaley/Taiwan-Drivers-License-Exam-Anki/tree/main/pdfs) for the list of input PDFs).
These `.apkg` files can be imported into Anki.

## Difficulty

* hard - A question that you could easily get wrong if you don't study.
* medium - A question that you could get wrong if you don't have experience driving in another country, OR a question that is easy but has tricky wording.
* easy - A question where the answer is intuitive.
* unknown_difficulty - The difficulty hasn't been tagged yet. I welcome contributions / pull requests to tag the difficulty for these questions!

For most test takers; I'd recommend only studying the hard questions. For people who are completely new to driving, I'd recommend also studying the medium questions.
Don't bother with the easy questions; they aren't worth your time, I promise.

### Examples

Questions with answers like 1, 2, or 3 years, or 100, 200, 300 meters, are all ranked hard.

## Limitations

This deck doesn't include questions for mechanical knowledge (which you don't need if you just want a regular motorcycle or car license), or for large/specialized vehicles.
It also doesn't include "situational" questions (part of the motorcycle exam), which are all easy and probably not worth studying. If you want to see these questions, you can
[download them here](https://www.thb.gov.tw/file.ashx?id=c57b175b-3f3e-4da4-827b-da51fef79a8a).

## Differences from `drive-taiwan`

- Update PDFs to the latest versions (from January 2020).
- Use genanki to generate output, which allows controlling the formatting of the cards.
- Support copying question difficulty values from existing questions when re-generating from a new PDF.
- Convert PDF data into an intermediate YAML format, which can be re-used by other projects.
These generated YAML files are checked-in (see the [yamls directory](https://github.com/kerrickstaley/Taiwan-Drivers-License-Exam-Anki/tree/main/yamls))
so you don't need to run the code in this repo to use them.
- Tag difficulty on more questions.
- Remove support for generating HTML versions of PDFs.
- Remove support for Chinese-language PDFs.
