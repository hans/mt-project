"""Annotates Spanish-language text."""

from nltk import BigramTagger, UnigramTagger
from nltk.corpus import cess_esp


TAGGER = None


def get_tagger():
    global TAGGER
    if TAGGER is None:
        # TODO: Load tagger from pickled form
        training_data = cess_esp.tagged_sents()
        unigram_tagger = UnigramTagger(training_data)
        bigram_tagger = BigramTagger(training_data, backoff=unigram_tagger)

        TAGGER = bigram_tagger

    return TAGGER


def tag(sentence_tokens):
    """For a given token list, return a list of `(word, tag)` pairs,
    where `tag` is in a format which matches the EAGLES tagset[1].

    [1]: http://nlp.lsi.upc.edu/freeling/doc/tagsets/tagset-es.html
    """

    return get_tagger().tag(sentence_tokens)
