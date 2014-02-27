# -*- coding: utf-8-*-
# Grammatical Expansion

# e.g. expand_verb('vmip3p0',['have','hold'])
def expand_verb(tag,en_list):
    """ Takes a verb with a POS tag and adds pronoun to the words in the
    en_list """


    if tag[0] == 'v':
        tiempo = tag[3]
        persona = tag[4]
        numero = tag[5]
        # genero = tag[6]

        if persona == '1':
            pronoun = 'I ' if numero == 's' else 'we '
        elif persona == '2':
            pronoun = 'you '
        elif persona == '3':
            pronoun = 'he ' if numero == 's' else 'they '
            # sorry for being sexist
        else:
            pronoun = ''

        final_s = lambda en_word: ('es' if en_word[-1] == 's' else 's') \
              if persona == '3' and numero == 's' and tiempo == 'p' else ''
            
        return [pronoun + en_word + final_s(en_word) for en_word in en_list]
    else:
        return en_list
