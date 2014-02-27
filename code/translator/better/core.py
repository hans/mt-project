"""Defines a translator that is, er, better than the baseline. Hence the
name.

TODO: remove awkwardness"""

import copy
import itertools

from translator.direct import DirectTranslator
from translator.better import preprocessing, postprocessing


class BetterTranslator(DirectTranslator):

    PREPROCESSING_PIPELINE = [
        preprocessing.annotate_pos,

        preprocessing.join_phrases
    ]

    def preprocess(self, sentence):
        """Given a list of tokens from a source language sentence,
        preprocess the tokens. Returns a tuple of the form
        `(preprocessed_sentence, annotations)`

        TODO: describe annotations result"""

        annotations = {}
        for step in self.PREPROCESSING_PIPELINE:
            sentence, annotations = step(sentence, annotations)

        return sentence, annotations


    POSTPROCESSING_PIPELINE = [
        postprocessing.pick_best_candidate
    ]

    def postprocess(self, source_annotations, data):
        """Thread data through the postprocessing pipeline. Returns the
        result of the final step of the pipeline."""

        for step in self.POSTPROCESSING_PIPELINE:
            data = step(source_annotations, data)

        return data

    def translate(self, sentence):
        sentence, source_annotations = self.preprocess(sentence)

        # Perform direct translation
        candidate_words = (super(BetterTranslator, self)
                           .get_candidate_words(sentence))

        candidate_sentences = list(itertools.product(*candidate_words))

        # Now build a list of `(candidate_sentence, annotations)` pairs
        postprocessing_data = [(candidate, {})
                               for candidate in candidate_sentences]
        postprocessing_data = self.postprocess(source_annotations,
                                               postprocessing_data)

        if not postprocessing_data:
            return None

        # TODO: ' '.join(..) is not optimal
        return ' '.join(postprocessing_data[0][0])


class PerClauseTranslator(BetterTranslator):
    def __init__(self, *args, **kwargs):
        super(PerClauseTranslator, self).__init__(*args, **kwargs)

    CLAUSE_BOUNDARIES = [',', 'que', 'y']

    def get_clauses(self, tokens):
        """Split a list of Spanish tokens into separate clauses. Yields
        values of the form `(clause, separator)`, where `clause` is a
        list of tokens in the yielded clause and `separator` is the
        token used to separate this clause from the next (potentially
        null)."""

        result = []
        for token in tokens:
            if token in self.CLAUSE_BOUNDARIES:
                yield result, token
                result = []
            else:
                result.append(token)

        yield result, None

    def translate(self, sentence):
        result = []
        for clause, boundary in self.get_clauses(sentence):
            result.append(super(PerClauseTranslator, self).translate(clause))

            if boundary is not None:
                result.append(super(PerClauseTranslator, self)
                              .translate([boundary]))

        return ' '.join(result)
