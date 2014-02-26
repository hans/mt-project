"""Defines a translator that is, er, better than the baseline. Hence the
name.

TODO: remove awkwardness"""


from translator.direct import DirectTranslator
from translator.better import preprocessing


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

    def translate(self, sentence):
        sentence, annotations = self.preprocess(sentence)

        # Perform direct translation
        #
        # TODO: just call super().get_candidate_words(), and then run
        # postprocessing
        translated = super(BetterTranslator, self).translate(sentence)

        return translated
