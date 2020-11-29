# Taiwan Driver's License Anki Deck

This repo contains code to generate an [Anki](https://apps.ankiweb.net/) flashcard deck which helps you study for the exams for Taiwan's scooter and car driver's licenses.

It uses the [official question bank PDFs](https://www.thb.gov.tw/sites/ch/modules/download/download_list?node=d78b410f-a497-4cbe-83d9-b7e7ad7b052e&c=e94977a2-5a11-45ce-b530-5ca55d709ed3).

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

* impossible - Like hard, but harder.
* hard - A question that you could easily get wrong if you don't study.
* medium - A question that you could get wrong if you don't have experience driving in another country, OR a question that is easy but has tricky wording.
* easy - A question where the answer is intuitive.
* unknown_difficulty - The difficulty hasn't been tagged yet. I welcome contributions / pull requests to tag the difficulty for these questions!

For most test takers; I'd recommend only studying the hard and impossible questions. For people who are completely new to driving, I'd recommend also studying the medium questions.
Don't bother with the easy questions; they aren't worth your time, I promise.

### Examples

Questions with answers like 1, 2, or 3 years, or 100, 200, 300 meters, are all ranked hard.

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
