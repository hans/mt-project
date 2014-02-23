# -*- coding: utf-8 -*-

import sys
import os
import itertools

from nltk.tokenize import word_tokenize

class MT_ES_EN:
  def __init__(self):
    self.ES_EN_dict = {}
    self.ES_sentences = []
    self.EN_sentences = []

  def readSentences(self, fileName):
    """
    Called by directTranslation in reading Spanish sentences into memory.
    """
    f = open(fileName)
    for line in f:
      # Clean line
      line = line.replace('—', '--')
      line = line.replace('…', '...')
      line = line.replace('¿', '¿ ')

      words = word_tokenize(line)
      self.ES_sentences.append(words)
    f.close()

  def buildDict(self, fileName):
    """
    Called by directTranslation in building the Spanish-English dictionary.
    """
    f = open(fileName)
    for line in f:
      entry = line.split(,)
      self.ES_EN_dict[entry[0]] = entry[1:]

  def directTranslation(self, sentenceFile, dictFile):
    """
    Takes Spanish text and a dictionary file, performs direct translation,
    storing the result in self.EN_sentences (and printing it out for now)
    """
    self.readSentences(sentenceFile)
    self.buildDict(dictFile)
    for ES_sentence in self.ES_sentences:
      EN_words = [self.ES_EN_dict.get(ES_word.lower(), [ES_word])
                  for ES_word in ES_sentence]
      self.EN_sentences.append(EN_words)

    self._printTopCandidates()

  def _printTopCandidates(self):
    """
    Print the top candidate translation for each sentence in the corpus.
    """

    for sentence_data in self.EN_sentences:
      candidates = itertools.product(*sentence_data)
      print ' '.join(next(candidates))


def main():
  if len(sys.argv) != 3:
    print "Usage: 'python translator.py original_text.txt dictFile.txt'"
    return
  if not os.path.isfile(sys.argv[1]):
    print "Original text file is invalid"
    return
  if not os.path.isfile(sys.argv[2]):
    print "Dictionary file is invalid"
    return

  translator = MT_ES_EN()
  translator.directTranslation(sys.argv[1], sys.argv[2])

if __name__ == "__main__":
    main()
