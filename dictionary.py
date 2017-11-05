import json
import requests

OD_TRANSLATE = 'https://od-api.oxforddictionaries.com:443/api/v1/entries/de/{word}/translations=en'
OD_LEMMATRON = 'https://od-api.oxforddictionaries.com:443/api/v1/inflections/de/{word}'


class Dictionary:
    def __init__(self, config_vars):
        self._headers = config_vars

    def lookup_json(self, word):
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

    def lookup_html(self, word):
        # use the already written json code, then pass it into a DictEntry object.
        # but we're not using that right now

        # entry_json, status_code = self.lookup_json(word)
        status_code = 200
        entry_json = "{\"category\": \"noun\", \"grammar\": [{\"Gender\": \"Feminine\", \"Case\": \"Dative\", \"Number\": \"Singular\"}, {\"Gender\": \"Feminine\", \"Case\": \"Genitive\", \"Number\": \"Singular\"}, {\"Gender\": \"Feminine\", \"Case\": \"Accusative\", \"Number\": \"Singular\"}], \"de\": \"Sahne\", \"en\": [\"cream\"], \"root\": \"Sahne\"}"
        return DictEntry(json.loads(entry_json), status_code)


class DictEntry:
    def __init__(self, entry_json, status_code):
        self._json = entry_json
        if status_code == 200:
            self.found = True
            self.category = entry_json['category']
            self.de = entry_json['de']
            self.root = entry_json['root']
            self.grammar_string = gen_grammar_string(entry_json['category'], entry_json['root'], entry_json['grammar'])
            self.en_string = gen_english_string(entry_json['en'])


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


def gen_english_string(english):
    en_string = ''
    for word in english:
        en_string = en_string + ', ' + word
    en_string = en_string[2:len(en_string)]
    return en_string

def gen_grammar_string(category, root, grammar):
    if category == 'noun':
        return gen_noun_string(grammar[0], root)


def gen_noun_string(grammar, root):
    if grammar['Number'] == 'Singular':
        return "Singular noun, {}". format(grammar['Gender'].lower())
    else:
        return "Plural form of: <i>{}</i>".format(root)


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

