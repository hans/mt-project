import itertools

from translator.core import Translator

class DirectTranslator(Translator):
    """A `Translator` which performs naive word-to-word translation of
    the source text.

    Serves as the baseline algorithm for this exercise."""

    def get_candidate_words(self, sentence):
        """Returns a list of lists, where each sublist at index `i`
        contains all the possible direct translations of the source
        language word at `sentence[i]`."""

        return [self.dictionary.get(word.lower(), [word])
                for word in sentence]

    def translate(self, sentence):
        candidate_words = self.get_candidate_words(sentence)
        candidate_sentences = itertools.product(*candidate_words)

        # Blindly choose the first value of every sublist
        candidate = next(candidate_sentences)
        return ' '.join(candidate)
