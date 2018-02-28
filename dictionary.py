import json
import requests
import spacy
import os

OD_TRANSLATE = 'https://od-api.oxforddictionaries.com:443/api/v1/entries/de/{word}/translations=en'
OD_LEMMA = 'https://od-api.oxforddictionaries.com:443/api/v1/inflections/de/{word}'

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

TAG_DICT = {}

for pos in POS_DICT:
    for tag in POS_DICT[pos]:
        TAG_DICT[tag] = pos


class Dictionary:
    def __init__(self, config_vars):
        self._headers = config_vars

    def lookup(self, word, root, pos):
        r = requests.get(OD_TRANSLATE.format(word=root), headers=self._headers)
        if r.status_code == 200:
            r_json = r.json()['results']
            for lexEntry in r_json[0]['lexicalEntries']:
                if lexEntry['lexicalCategory'].lower() == pos.lower():
                    translations = self.sort_english(lexEntry['entries'])
                    if len(translations) != 0:
                        grammar = self.get_grammar(word, pos)
                        return True, translations, grammar
        return False, [], []

    def get_grammar(self, word, pos):
        r = requests.get(OD_LEMMA.format(word=word), headers=self._headers)
        if r.status_code == 200:
            r_json = r.json()['results']
            for lexEntry in r_json[0]['lexicalEntries']:
                if lexEntry['lexicalCategory'].lower() == pos.lower():
                    return self.sort_grammar(lexEntry['grammaticalFeatures'])
        return []

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


dict_config = {'app_id': os.environ.get('APP_ID'), 'app_key': os.environ.get('APP_KEY')}

dictionary = Dictionary(dict_config)


class DictEntry:
    def __init__(self, word, lemma, tag):
        self.word = word
        self.root = lemma
        self.tag = tag
        self.pos = TAG_DICT[tag]
        if self.pos in ['Noun', 'Verb', 'Adjective', 'Unknown']:
            self.css_cat = self.pos.lower()
        else:
            self.css_cat = 'other'

        if self.pos not in ['Proper Noun', 'Other', 'Numeral']:
            self.found, translation, grammar = dictionary.lookup(word, lemma, self.pos)
            if self.found:
                self.english = self.gen_english_string(translation)
                self.grammar_features = self.list_features(grammar)
            else:
                self.english = 'No translation found'
                self.grammar_features = []

        else:
            self.found = False
            self.english = 'Not translatable'
            self.grammar_features = []
        self.grammar_explanation = spacy.explain(tag)



    @staticmethod
    def gen_english_string(english):
        en_string = ''
        for word in english:
            en_string = en_string + ', ' + word
        en_string = en_string[2:len(en_string)]
        return en_string


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


if __name__ == '__main__':
    trains = DictEntry("Züge", "Zug", "NN")
    print(trains.grammar_features)
    print(trains.english)
    print("Done")
