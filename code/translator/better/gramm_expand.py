# -*- coding: utf-8-*-
# Grammatical Expansion

# This should happen AFTER word order has been rearranged to
# be more English-like

# e.g. expand_verb('vmip3p0',['have','hold'],True)
def expand_verb(tag,en_list,use_pronoun):
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
                pronoun = 'he ' if numero == 's' else 'they '
                # sorry for being sexist


        final_s = lambda en_word: ('es' if en_word[-1] == 's' else 's') \
              if persona == '3' and numero == 's' and tiempo == 'p' else ''
            
        return [pronoun + en_word + final_s(en_word) for en_word in en_list]
    else:
        return en_list

def expand_sent(tags,en_lists):
    """Takes the pos tags of a sentence, looks for verbs, and expands
    them, deciding whether or not they need the pronoun"""
    
    simp_tags = [tag[0] for tag in tags]
    for i,simp_tag in enumerate(simp_tags):
        if simp_tag == 'v':
            use_pronoun = 'n' not in simp_tags[:i] and 'p' not in simp_tags[:i]
            en_lists[i] = expand_verb(tags[i],en_lists[i],use_pronoun)
        # elif simp_tag == 's':
        #     en_lists[i].append('')
    return en_lists

def gramm_expand(sentences,annotations):
    """Formats everything correctly for the contract"""
    for sentence in sentences:
        posses = annotations['pos'] # Spanish parts of speech
        list_sent = [[word] for word in sentence]
        return ([word[0] for word in expand_sent(posses,list_sent)],annotations)
    
    
#print expand_sent(['pp1csn00','sps00','vmip3p0'],[['I'],['to','for'],['have','hold']])

print gramm_expand([['to','have'],['to','hold']],{'pos':['sps00','vmip3p0']})


