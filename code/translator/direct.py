from core import Translator

class DirectTranslator(Translator):
    """A `Translator` which performs naive word-to-word translation of
    the source text.

    Serves as the baseline algorithm for this exercise."""

    def translate(self, sentence):
        return [self.dictionary.get(word.lower(), [word])
                for word in sentence]
