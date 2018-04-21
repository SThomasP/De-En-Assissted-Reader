import json
import requests
import spacy
import os

# the domains for looking stuff up in the api
OD_TRANSLATE = 'https://od-api.oxforddictionaries.com:443/api/v1/entries/de/{word}/translations=en'
OD_LEMMA = 'https://od-api.oxforddictionaries.com:443/api/v1/inflections/de/{word}'

# Which fine POS are part of which coarse POS
POS_DICT = {'Adjective': ['ADJA', 'ADJD'],
            'Preposition': ['APPO', 'APPR', 'APPRART', 'APZR'],
            'Adverb': ['ADV', 'PAV', 'PROAV', 'PWAV'],
            'Auxiliary Verb': ['VAFIN', 'VAIMP', 'VAINF', 'VAPP'],
            'Conjugation': ['KOKOM', 'KON', 'KOUI', 'KOUS'],
            'Determiner': ['ART', 'PDAT', 'PIAT', 'PIDAT', 'PPOSAT', 'PRELAT', 'PWAT'],
            'Interjection': ['ITJ'],
            'Noun': ['NN'],
            'Numeral': ['CARD'],
            'Particle': ['PTKA', 'PTKANT', 'PTKNEG', 'PTKVZ', 'PTKZU'],
            'Pronoun': ['PDS', 'PIS', 'PPER', 'PPOSS', 'PRELS', 'PRF', 'PWS'],
            'Proper Noun': ['NE', 'NNE'],
            'Other': ['FM', 'TRUNC', 'XY'],
            'Verb': ['VMFIN', 'VMINF', 'VMPP', 'VVFIN', 'VVIMP', 'VVINF', 'VVIZU', 'VVPP']}

# lookup coarse pos from fine pos
TAG_DICT = {}

# generate TAG_DICT from POS_DICT
for pos in POS_DICT:
    for tag in POS_DICT[pos]:
        TAG_DICT[tag] = pos


# dictionary lookup
class Dictionary:
    def __init__(self, config_vars):
        self._headers = config_vars

    # lookup a word in the dictionary
    def lookup(self, word, root, pos):
        # get the translations of the root word
        r = requests.get(OD_TRANSLATE.format(word=root), headers=self._headers)

        # if they're found, extract them
        if r.status_code == 200:
            r_json = r.json()['results']
            for lexEntry in r_json[0]['lexicalEntries']:
                if lexEntry['lexicalCategory'].lower() == pos.lower():
                    translations = self.sort_english(lexEntry['entries'])
                    if len(translations) != 0:
                        # then try and get grammatical features
                        grammar = self.get_grammar(word, pos)
                        return True, translations, grammar
        return False, [], []

    # get the grammatical features of the word
    def get_grammar(self, word, pos):
        # look it up in the api.
        r = requests.get(OD_LEMMA.format(word=word), headers=self._headers)
        if r.status_code == 200:
            r_json = r.json()['results']
            # find the correct usage of the word
            for lexEntry in r_json[0]['lexicalEntries']:
                if lexEntry['lexicalCategory'].lower() == pos.lower():
                    # sort the grammar
                    return self.sort_grammar(lexEntry['grammaticalFeatures'])
        return []

    # sort the grammar into possible use cases.
    @staticmethod
    def sort_grammar(gram_fe):
        counter = {}
        # count the occurrences of each grammatical type
        for feature in gram_fe:
            g_type = feature['type'].lower()
            if g_type in counter.keys():
                counter[g_type] += 1
            else:
                counter[g_type] = 1
        # determine the maximum
        if counter == {}:
            return []
        maximum = max(counter, key=(lambda key: counter[key]))
        # create the empty dictionaries
        sorted = [{} for _ in range(counter[maximum])]

        # create another dictionary to keep track of how many times a type has occurred while sorting.
        occurred = {}
        for key in counter.keys():
            occurred[key] = 0

        # sort the features
        for i in range(len(gram_fe)):
            g_type = gram_fe[i]['type'].lower()
            text = gram_fe[i]['text'].lower()
            o = occurred[g_type]
            sorted[o][g_type] = text
            if o == counter[g_type] - 1:
                for j in range(o, len(sorted)):
                    sorted[j][g_type] = text
            occurred[g_type] += 1

        # some stuff that has to be coded manually
        if 'person' in sorted[0].keys() and 'number' in sorted[0].keys() and len(sorted) >= 2:
            if sorted[0]['person'] == 'second' and sorted[1]['person'] == 'third':
                sorted[0]['person'] = 'third'
                sorted[1]['person'] = 'second'

        if 'degree' in sorted[0].keys() and len(sorted) > 1:
            if sorted[0]['degree'] == 'positive' and sorted[1]['degree'] == 'comparative':
                sorted[0]['degree'] = 'comparative'
                sorted[1]['degree'] = 'positive'

        return sorted

    # iterate through the uses of a word, looking for translations
    @staticmethod
    def sort_english(entries):
        en = []
        for entry in entries:
            if 'senses' in entry.keys():
                senses = entry['senses']
                for sense in senses:
                    if 'translations' in sense.keys():
                        translations = sense['translations']
                        for translation in translations:
                            en.append(translation['text'])
        return en


# get the config information from the environment variables.
dict_config = {'app_id': os.environ.get('APP_ID'), 'app_key': os.environ.get('APP_KEY')}

# load the dictionary
dictionary = Dictionary(dict_config)


# an individual entry of the dictionary
class DictEntry:
    # create the dictionary entry entry
    def __init__(self, word, lemma, tag):
        self.word = word
        self.root = lemma
        self.tag = tag
        self.pos = TAG_DICT[tag]
        # set the css class
        if self.pos in ['Noun', 'Verb', 'Adjective', 'Unknown']:
            self.css_cat = self.pos.lower()
        else:
            self.css_cat = 'other'
        # if there can be a translation, look it up and save it
        if self.pos not in ['Proper Noun', 'Other', 'Numeral']:
            self.found, translation, grammar = dictionary.lookup(word, lemma, self.pos)
            if self.found:
                self.english = self.gen_english_string(translation)
                self.grammar_features = self.list_features(grammar)
            else:
                self.english = 'No translation found'
                self.grammar_features = []

        # if it is not possible for the word to have a translation, don't bother.
        else:
            self.found = False
            self.english = 'Not translatable'
            self.grammar_features = []

        # get a tag explanation from SpaCy
        self.grammar_explanation = spacy.explain(tag)

    # convert the list of translations provided by the dictionary into something human readable
    @staticmethod
    def gen_english_string(english):
        en_string = ''
        for word in english:
            en_string = en_string + ', ' + word
        en_string = en_string[2:len(en_string)]
        return en_string

    # convert the grammar use cases provided by the dictionary into something human readable
    @staticmethod
    def list_features(grammar):
        grammar_list = []
        for instance in grammar:
            grammar_string = ''
            for feature in instance.keys():
                grammar_string = grammar_string + '{}: {}, '.format(feature.capitalize(), instance[feature])
            grammar_string = grammar_string[:-2:]
            grammar_list.append(grammar_string)
        return grammar_list


# test lookup
if __name__ == '__main__':
    trains = DictEntry("Zug", "Zug", "NN")
    print(trains.grammar_features)
    print(trains.english)
    print("Done")
