import sys
import getopt
import os

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
      words = word_tokenize(line)
      self.ES_sentences.append(words)
    f.close()

  def buildDict(self, fileName):
    """
    Called by directTranslation in building the Spanish-English dictionary.
    """
    f = open(fileName)
    for line in f:
      entry = line.split()
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
    print self.EN_sentences

"""
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
"""
