import json
import requests

OD_TRANSLATE = 'https://od-api.oxforddictionaries.com:443/api/v1/entries/de/{word}/translations=en'
OD_LEMMATRON = 'https://od-api.oxforddictionaries.com:443/api/v1/inflections/de/{word}'

class Dictionary:
    def __init__(self, config_vars):
        self._headers = config_vars

    def lookup(self, word):
        entry = {'de': word, 'en': [], 'root': '', 'category': '', 'grammar': []}
        initial_entry = {'de': word, 'en': [], 'root': '', 'category': '', 'grammar': []}
        in_dict, entry = self._lemmatron(entry)
        if in_dict:
            en_found, entry = self._lookup_online(entry)
            if en_found:
                return json.dumps(entry, ensure_ascii=False), 200
            else:
                return json.dumps(initial_entry, ensure_ascii=False), 404
        else:
            return json.dumps(initial_entry, ensure_ascii=False), 404





    def _lemmatron(self, entry):
        word = entry['de'].lower()
        r = requests.get(OD_LEMMATRON.format(word=word), headers=self._headers)
        if r.status_code == 200:
            r_json = r.json()['results']
            entry['root'] = r_json[0]['lexicalEntries'][0]['inflectionOf'][0]['text']
            entry['category'] = r_json[0]['lexicalEntries'][0]['lexicalCategory'].lower()
            entry['grammar'] = sort_grammar(r_json[0]['lexicalEntries'][0]['grammaticalFeatures'])
            return True, entry
        else:
            return False, entry


    def _lookup_online(self, entry):
        word = entry['root']
        cat = entry['category']
        r = requests.get(OD_TRANSLATE.format(word=word), headers=self._headers)
        if r.status_code == 200:
            r_json = r.json()['results']
            for lexEntry in r_json[0]['lexicalEntries']:
                if lexEntry['lexicalCategory'].lower() == cat:
                    entry['en'] = sort_english(lexEntry['entries'])
                    if len(entry['en']) != 0:
                        return True, entry
            return False, entry
        else:
            return False, entry



def sort_grammar(gram_fe):
    counter = {}
    # count the occurrences of each grammatical type
    for feature in gram_fe:
        g_type = feature['type']
        if g_type in counter.keys():
            counter[g_type] += 1
        else:
            counter[g_type] = 1
    # determine the maximum
    maximum = max(counter, key=(lambda key: counter[key]))
    # create the empty dictionaries
    sorted = [{} for _ in range(counter[maximum])]

    # create another dictionary to keep track of how many times a type has occurred while sorting.
    occurred = {}
    for key in counter.keys():
        occurred[key] = 0

    # sort the features
    for i in range(len(gram_fe)):
        g_type = gram_fe[i]['type']
        text = gram_fe[i]['text']
        o = occurred[g_type]
        sorted[o][g_type] = text
        if o == counter[g_type] - 1:
            for j in range(o, len(sorted)):
                sorted[j][g_type] = text
        occurred[g_type] += 1

    return sorted


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

