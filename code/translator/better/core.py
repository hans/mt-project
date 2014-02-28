"""Defines a translator that is, er, better than the baseline. Hence the
name.

TODO: remove awkwardness"""

import itertools
import operator

from translator.direct import DirectTranslator
from translator.better import preprocessing, postprocessing, gramm_expand


class BetterTranslator(DirectTranslator):

    PREPROCESSING_PIPELINE = [
        preprocessing.annotate_pos,
        preprocessing.join_phrases,
        preprocessing.revert_by_pos('n......', 'a.....'),
        preprocessing.revert_by_pos(None, 'a.....'),
        preprocessing.revert_by_pos('pp...[^0no]..', 'v......'),
    ]

    def preprocess(self, sentence):
        """Given a list of tokens from a source language sentence,
        preprocess the tokens. Returns a tuple of the form
        `(preprocessed_sentence, annotations)`

        TODO: describe annotations result"""

        annotations = {}
        for step in self.PREPROCESSING_PIPELINE:
            print '\t\tPreprocessing: ', step
            sentence, annotations = step(sentence, annotations)

        return sentence, annotations


    POSTPROCESSING_PIPELINE = [
        postprocessing.fix_demonstratives,
        # gramm_expand.prep_homicide,
        gramm_expand.gramm_expand,
        postprocessing.fix_an,
        postprocessing.fix_dont,
        postprocessing.dont_in_verb,
        postprocessing.pick_best_candidate
    ]

    def postprocess(self, source_annotations, data):
        """Thread data through the postprocessing pipeline. Returns the
        result of the final step of the pipeline."""


        for step in self.POSTPROCESSING_PIPELINE:
            print '\t\tPostprocessing: ', step
            data = step(source_annotations, data)

        return data

    def join_tokens(self, tokens):
        """Return a list of tokens which can be joined with the empty
        string."""

        for t1, t2 in zip(tokens, tokens[1:] + ['']):
            space = True
            if t2 in ['', ',', '.', '!', '?']:
                space = False

            yield '{}{}'.format(t1, ' ' if space else '')

    def translate(self, sentence):
        print ' '.join(sentence[:8]) + ' ... ' + ''.join(sentence[-1:])
        print '\tInitializing preprocessing'
        sentence, source_annotations = self.preprocess(sentence)

        # Perform direct translation
        candidate_words = (super(BetterTranslator, self)
                           .get_candidate_words(sentence))

        product_size = reduce(operator.mul,
                              [len(cands) for cands in candidate_words])

        print '\tCalculating Cartesian product (size: ', product_size, ')'
        candidate_sentences = list(itertools.product(*candidate_words))

        # Now build a list of `(candidate_sentence, annotations)` pairs
        print '\tInitiating postprocessing'
        postprocessing_data = [(candidate, {})
                               for candidate in candidate_sentences]
        postprocessing_data = self.postprocess(source_annotations,
                                               postprocessing_data)

        if not postprocessing_data:
            return None

        print '\tDone'

        return ''.join(self.join_tokens(postprocessing_data[0][0]))


class PerClauseTranslator(BetterTranslator):
    def __init__(self, *args, **kwargs):
        super(PerClauseTranslator, self).__init__(*args, **kwargs)

    # Should these tokens precede what might be marked as a clause
    # boundary, the succeeding token should never be considered a clause
    # boundary
    CLAUSE_NON_BOUNDARY_PREFIXES = ['lo', 'de', 'es']

    CLAUSE_BOUNDARIES = [',', 'que', 'y']

    def get_clauses(self, tokens):
        """Split a list of Spanish tokens into separate clauses. Yields
        values of the form `(clause, separator)`, where `clause` is a
        list of tokens in the yielded clause and `separator` is the
        token used to separate this clause from the next (potentially
        null)."""

        result = []
        ignore_next = False

        for token in tokens:
            if token in self.CLAUSE_BOUNDARIES and not ignore_next:
                # Don't yield an empty clause
                if result:
                    yield result, token
                    result = []
                else:
                    result.append(token)
            else:
                result.append(token)

            ignore_next = token in self.CLAUSE_NON_BOUNDARY_PREFIXES

        if result:
            yield result, None

    def translate(self, sentence):
        result = []
        for clause, boundary in self.get_clauses(sentence):
            result.append(super(PerClauseTranslator, self).translate(clause))

            if boundary is not None:
                result.append(super(PerClauseTranslator, self)
                              .translate([boundary]))

        ret = ''.join(self.join_tokens(result))
        if ret:
            ret = ret[0].upper() + ret[1:]

        return ret
