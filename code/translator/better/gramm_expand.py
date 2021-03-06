# -*- coding: utf-8-*-
# Grammatical Expansion

# This should happen AFTER word order has been rearranged to
# be more English-like

def get_conjugated_ending(verb, tag):
    tiempo = tag[3]
    persona = tag[4]
    numero = tag[5]

    if (persona == '3' and numero == 's' and tiempo == 'p'
        and verb != 'is' and verb[-2:] != 'es'):
        if verb[-1] == 's':
            return 'es'
        else:
            return 's'
    return ''

# e.g. expand_verb('vmip3p0',['have','hold'],True)
def expand_verb(tag, en_list, use_pronoun):
    """ Takes a verb with a POS tag and adds pronoun to the words in the
    en_list """

    if tag[0] == 'v':
        tiempo = tag[3]
        persona = tag[4]
        numero = tag[5]
        # genero = tag[6]

        pronoun = ''
        if use_pronoun:
            if persona == '1':
                pronoun = 'I ' if numero == 's' else 'we '
            elif persona == '2':
                pronoun = 'you '
            elif persona == '3':
                pronoun = '' if numero == 's' else 'they '

        return [pronoun + en_word + get_conjugated_ending(en_word, tag)
                for en_word in en_list]
    else:
        return en_list

def expand_sent(tagged_tokens,en_lists):
    """Takes the pos tags of a sentence, looks for verbs, and expands
    them, deciding whether or not they need the pronoun"""

    full_tags = [(tag or None) for _, tag in tagged_tokens]
    simp_tags = [((tag and tag[0]) or None) for _, tag in tagged_tokens]
    for i, (t, tag) in enumerate(tagged_tokens):
        if tag and tag.startswith('v') and (not tag[2] == 'p'):
            use_pronoun = ('n' not in simp_tags[:i] and 'p' not in simp_tags[:i]
                           and not any('this' in en_list for en_list in en_lists[:i + 2]))
            en_lists[i] = expand_verb(tagged_tokens[i][1], en_lists[i],
                                      use_pronoun)
        # elif simp_tag == 's':
        #     en_lists[i].append('')
    return en_lists

def gramm_expand(annotations,data):
    """Formats everything correctly for the contract"""
    #print '>>>>','annotations',annotations,'data',data
    # sometimes annotations and data are flipped with each other
    # if type(annotations) == type([]):
    #     sentence_list = annotations
    #     pos_list = data['pos']
    # else:
    sentence_list = [tup[0] for tup in data]
    pos_list = annotations['pos']

    for i,sent in enumerate(sentence_list):
        sentence_list[i] = expand_sent(pos_list,[[word] for word in sent])
        sentence_list[i] = ([word[0] for word in sentence_list[i]],{})
        # print "sli",sentence_list[i]

        #print sentence_list
    return sentence_list


def prep_homicide(annotations,data):
    """Runs through each preposition in the sentence and makes a duplicate
    sentence without that preposition (it is replaced by an empty
    string)"""
    simp_tags = [tup[1][0] if tup[1] != None else '' for tup in annotations['pos']]
    data2 = []
    for i,tag in enumerate(simp_tags):
        if tag == 's':
            for sentence, annotations in data:
                new_sent = sentence[:i] + [''] + sentence[i+1:]
                data2.append((new_sent, annotations))

    return data + data2


#print expand_sent(['pp1csn00','sps00','vmip3p0'],[['I'],['to','for'],['have','hold']])

#print gramm_expand([['to','have'],['to','hold']],{'pos':['sps00','vmip3p0']})
