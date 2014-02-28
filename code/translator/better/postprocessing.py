# -*- coding: utf-8 -*-
"""Defines postprocessing operations -- functions which operate on and
annotate candidate sentences.

Functions in this module are threaded together into a pipeline in
`translator.better.core`. They must satisfy a simple contract,
expressible with a simple type signature:

    postprocessor :: SourceAnn -> [(Sent, Ann)] -> [(Sent, Ann)]

That is, each postprocessor function accepts source annotations and a
list of `(sentence, annotation)` tuples (where each `sentence` is a list
of tokens and each `annotation` is an arbitrary `dict` containing data
about the corresponding sentence) and returns a list of the same form,
possibly with fewer or more tuples and possibly with the given tuples
modified in some way."""

import math
import os
import sys
import itertools

class CustomLanguageModel:

  def __init__(self, corpus):
    """Initialize your data structures in the constructor."""
    self.unigram_dict = {}
    self.bigram_dict = {}
    self.trigram_dict = {}
    self.train(corpus)

  def train(self, corpus):
    """ Takes a corpus and trains your language model. 
        Compute any counts or other corpus statistics in this function.
    """  
   # Build dictionary of unigrams and counts
    num_words = 0
    for sentence in corpus:
        for word in sentence:
            num_words += 1
            if word in self.unigram_dict:
                self.unigram_dict[word] += 1
            else:
                self.unigram_dict[word] = 1

    # Add <unk>
    self.unigram_dict["<UNK>"] = 0
    print "Trained unigram model"

    # Calculate bigram counts
    bigram = ''
    for sentence in corpus:
        for i in xrange(0, len(sentence)-1): # subtract 1 for bigrams
            bigram = sentence[i] + ' ' + sentence[i+1]
            if bigram in self.bigram_dict:
                self.bigram_dict[bigram] += 1
            else:
                self.bigram_dict[bigram] = 1
    print "Trained bigram model"


    # Calculate trigram counts
    trigram = ''
    for sentence in corpus:
        for i in xrange(0, len(sentence)-2): # subtract 2 for trigrams
            trigram = sentence[i] + ' ' + sentence[i+1] + ' ' + sentence[i+2]
            if trigram in self.trigram_dict:
                self.trigram_dict[trigram] += 1
            else:
                self.trigram_dict[trigram] = 1
    print "Trained trigram model"


    # Build trigram unsmoothed log-probabilities
    trigram_prob = 0.0
    for trigram in self.trigram_dict:
        first_bigram = trigram.split()[0] + ' ' + trigram.split()[1]
        trigram_prob = math.log(self.trigram_dict[trigram]) - math.log(self.bigram_dict[first_bigram])
        self.trigram_dict[trigram] = trigram_prob

    print "Trigram probs"

    # Build bigram unsmoothed log-probabilities
    bigram_prob = 0.0
    for bigram in self.bigram_dict:
        bigram_prob = math.log(self.bigram_dict[bigram]) - math.log(self.unigram_dict[bigram.split()[0]])
        self.bigram_dict[bigram] = bigram_prob
    print "Bigram probs"

    # Build Laplace unigram log-probabilities
    word_prob = 0.0
    vocab_size = len(self.unigram_dict) # |V|
    for word in self.unigram_dict:
        word_prob = math.log(self.unigram_dict[word] + 1) - math.log(num_words + vocab_size)
        self.unigram_dict[word] = word_prob
    print "Unigram probs"

  def score(self, sentence):
    """ Takes a list of strings as argument and returns the log-probability of the 
        sentence using your language model. Use whatever data you computed in train() here.
    """
    log_prob = 0.0

    # Use bigrams for the beginning of the sentence
    bigram = sentence[0] + ' ' + sentence[1]
    if bigram in self.bigram_dict:
        log_prob += self.bigram_dict[bigram]
    elif len(bigram.split()) > 1:
        unigram = bigram.split()[1]
        if unigram in self.unigram_dict:
            log_prob += self.unigram_dict[unigram]
        else:
            log_prob += self.unigram_dict["<UNK>"]

    # Handle the rest of the sentence with stupid trigram backoff
    for i in xrange(0, len(sentence)-2): # -2 for trigrams
        trigram = sentence[i] + ' ' + sentence[i+1] + ' ' + sentence[i+2]
        bigram = sentence[i+1] + ' ' + sentence[i+2]
        unigram = sentence[i+2]
        if trigram in self.trigram_dict:
            log_prob += self.trigram_dict[trigram]
        elif bigram in self.bigram_dict:
            log_prob += self.bigram_dict[bigram]
        elif unigram in self.unigram_dict:
            log_prob += self.unigram_dict[unigram]
        elif len(unigram) > 0:
                log_prob += self.unigram_dict["<UNK>"]

    return log_prob

  def best_sentence(self, sentence_list):
    if len(sentence_list) == 0:
      return []

    bestScore = float('-inf')
    
    for i in xrange(0, len(sentence_list)):
      # Selects the maximum probability sentence here, according to the noisy channel model.
      currSentence = sentence_list[i][0][:]
      currScore = self.score(currSentence)
      print currSentence
      print currScore
      if currScore > bestScore:
        bestScore = currScore
        bestSentence = sentence_list[i]
    return bestSentence

def pick_best_candidate(source_ann, data):
    """The final postprocessing step which picks just one sentence from
    the candidate list."""
    path = '../../../corpus/data/'
    corpus = []
    for file in os.listdir(path):
        curr_file = os.path.join(path, file)
        if os.path.isfile(curr_file) and ".txt" in curr_file:
            file_contents = open(curr_file, 'r')
            corpus.extend(file_contents.read().split())

    EN_model = CustomLanguageModel(corpus)

    return EN_model.best_sentence(data)

