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

import copy
import math
import os
import sys
import itertools

from translator.better.gramm_expand import gramm_expand
from translator.better.preprocessing import join_phrases

VOWELS = ('a', 'e', 'i', 'o', 'u')
def fix_an(source_annotations, data):
    """Drop sentences which incorrectly use a/an."""

    result = []
    for sentence, annotations in data:
        drop = False
        for t1, t2 in zip(sentence, sentence[1:]):
            if t1 == 'a' and t2.startswith(VOWELS):
                drop = True
                break
            elif t1 == 'an' and not t2.startswith(VOWELS):
                drop = True
                break

        if not drop:
            result.append((sentence, annotations))

    return result


def fix_dont(source_ann, data):
    to_modify = []
    for i, ((source_t, _), (_, next_tag)) in enumerate(zip(source_ann['pos'],
                                                        source_ann['pos'][1:])):
        if source_t.lower() != 'no' or not next_tag or not next_tag.startswith('v'):
            continue

        to_modify.append(i)

    for sentence, annotations in data:
        for i in to_modify:
            sentence[i] = "don't"

    return data

def dont_in_verb(source_ann,data):
    """don't I write -> I don't write
    actually expanded for all adverbs"""

    pos_tags = source_ann['pos']

    length = len(pos_tags)

    def mark(i):
        return i < length - 2 \
            and pos_tags[i][1] and pos_tags[i][1][0] == 'r' \
            and pos_tags[i+1][1] and pos_tags[i+1][1][0] == 'v'

    dont_places = [i for i,tag in enumerate(pos_tags) \
                   if mark(i)]

    for sent_tup in data:
        sent = sent_tup[0]
        #print 'sent:',sent
        for i in dont_places:
            #sent = data[i][0]


            compound = sent[i+1].split() #assume it splits in two
            if len(compound) > 1:
                sent[i+1] = compound[0] +' '+ sent[i] +' '+ compound[1]
                sent[i] = ''
                data[i] = (sent,{})


    return data


def fix_demonstratives(source_ann, data):
    PHRASES = {
        (('no',), None, 'd.....|pp3fsa00'): ('not', None),
        (('the', 'our'), None, None): ('ours', None),
        (('the', 'ours'), None, None): ('ours', None),
        (('the', 'your'), None, None): ('yours', None),
        (('the', 'yours'), None, None): ('yours', None),
        (('the', 'my'), None, None): ('mine', None),
        (('the', 'mine'), None, None): ('mine', None),
        (('the', 'their'), None, None): ('theirs', None),
        (('the', 'theirs'), None, None): ('theirs', None),
    }

    ret = []
    for sentence, annotations in data:
        # Super hacky: pass in source annotations
        s, a = join_phrases(sentence, source_ann, PHRASES)
        ret.append((s, a))

    return ret


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

    # Calculate bigram counts
    bigram = ''
    for sentence in corpus:
        for i in xrange(0, len(sentence)-1): # subtract 1 for bigrams
            bigram = sentence[i] + ' ' + sentence[i+1]
            if bigram in self.bigram_dict:
                self.bigram_dict[bigram] += 1
            else:
                self.bigram_dict[bigram] = 1


    # Calculate trigram counts
    trigram = ''
    for sentence in corpus:
        for i in xrange(0, len(sentence)-2): # subtract 2 for trigrams
            trigram = sentence[i] + ' ' + sentence[i+1] + ' ' + sentence[i+2]
            if trigram in self.trigram_dict:
                self.trigram_dict[trigram] += 1
            else:
                self.trigram_dict[trigram] = 1


    # Build trigram unsmoothed log-probabilities
    trigram_prob = 0.0
    for trigram in self.trigram_dict:
        first_bigram = trigram.split()[0] + ' ' + trigram.split()[1]
        trigram_prob = math.log(self.trigram_dict[trigram]) - math.log(self.bigram_dict[first_bigram])
        self.trigram_dict[trigram] = trigram_prob

    # Build bigram unsmoothed log-probabilities
    bigram_prob = 0.0
    for bigram in self.bigram_dict:
        bigram_prob = math.log(self.bigram_dict[bigram]) - math.log(self.unigram_dict[bigram.split()[0]])
        self.bigram_dict[bigram] = bigram_prob

    # Build Laplace unigram log-probabilities
    word_prob = 0.0
    vocab_size = len(self.unigram_dict) # |V|
    for word in self.unigram_dict:
        word_prob = math.log(self.unigram_dict[word] + 1) - math.log(num_words + vocab_size)
        self.unigram_dict[word] = word_prob

  def score(self, sentence):
    """ Takes a list of strings as argument and returns the log-probability of the
        sentence using your language model. Use whatever data you computed in train() here.
    """
    log_prob = 0.0

    # Use unigram for single words
    if (len(sentence) == 0):
        return float('-inf')
    elif (len(sentence) == 1):
        if sentence[0] in self.unigram_dict:
            log_prob += self.unigram_dict[sentence[0]]
        else:
            log_prob += self.unigram_dict["<UNK>"]
        return log_prob

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

  def best_sentence(self, data):
    bestScore = float('-inf')
    bestSentence = None

    for i in xrange(0, len(data)):
      # Selects the maximum probability sentence here, according to the noisy channel model.
      currSentence = data[i][0][:]
      currScore = self.score(currSentence)
      # print currSentence
      # print currScore
      if currScore > bestScore:
        bestScore = currScore
        bestSentence = data[i]

    return bestSentence


EN_model = None

def pick_best_candidate(source_ann, data):
    """The final postprocessing step which picks just one sentence from
    the candidate list."""
    path = '../corpus/data/'
    corpus = []
    for file in os.listdir(path):
        curr_file = os.path.join(path, file)
        if os.path.isfile(curr_file) and ".txt" in curr_file:
            file_contents = open(curr_file, 'r')
            corpus.extend(file_contents.read().split())

    corpus_list = []
    corpus_list.append(corpus)

    global EN_model
    if EN_model is None:
        EN_model = CustomLanguageModel(corpus_list)

    return [EN_model.best_sentence(data)]
