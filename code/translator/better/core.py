"""Defines a translator that is, er, better than the baseline. Hence the
name.

TODO: remove awkwardness"""


from translator.core import Translator
from translator.better import preprocessing


class BetterTranslator(Translator):

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

        return [self.dictionary.get(word.lower(), [word])
                for word in sentence]
