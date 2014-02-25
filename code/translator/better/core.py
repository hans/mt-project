"""Defines a translator that is, er, better than the baseline. Hence the
name.

TODO: remove awkwardness"""


from translator.core import Translator


class BetterTranslator(Translator):
    def preprocess(self, sentence):
        """Given a list of tokens from a source language sentence,
        preprocess the tokens. Returns a tuple of the form
        `(preprocessed_sentence, annotations)`

        TODO: describe annotations result"""

        return sentence, []

    def translate(self, sentence):
        sentence, annotations = self.preprocess(sentence)

        return [self.dictionary.get(word.lower(), [word])
                for word in sentence]
