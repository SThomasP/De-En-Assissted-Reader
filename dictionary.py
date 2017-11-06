import json
import requests

OD_TRANSLATE = 'https://od-api.oxforddictionaries.com:443/api/v1/entries/de/{word}/translations=en'
OD_LEMMATRON = 'https://od-api.oxforddictionaries.com:443/api/v1/inflections/de/{word}'


class Dictionary:
    def __init__(self, config_vars):
        self._headers = config_vars

    def lookup_json(self, word):
        entry = {'de': word, 'en': [], 'root': '', 'category': '', 'grammar': []}
        in_dict, entry = self._lemmatron(entry)
        if in_dict:
            en_found, entry = self._lookup_online(entry)
            if en_found:
                return json.dumps(entry, ensure_ascii=False), 200
            else:
                return json.dumps(entry, ensure_ascii=False), 404
        else:
            return json.dumps(entry, ensure_ascii=False), 404

    def _lemmatron(self, entry):
        word = entry['de'].lower()
        r = requests.get(OD_LEMMATRON.format(word=word), headers=self._headers)
        if r.status_code == 200:
            r_json = r.json()['results']
            entry['category'] = r_json[0]['lexicalEntries'][0]['lexicalCategory'].lower()
            entry['grammar'] = self.sort_grammar(r_json[0]['lexicalEntries'][0]['grammaticalFeatures'])
            if entry['category'] == 'adjective' and entry['grammar'][0]['degree'] == "superlative":
                entry['root'] = r_json[0]['lexicalEntries'][0]['inflectionOf'][1]['text']
            else:
                entry['root'] = r_json[0]['lexicalEntries'][0]['inflectionOf'][0]['text']
            return True, entry
        else:
            entry['category'] = "unknown"
            return False, entry

    def _lookup_online(self, entry):
        word = entry['root']
        cat = entry['category']
        r = requests.get(OD_TRANSLATE.format(word=word), headers=self._headers)
        if r.status_code == 200:
            r_json = r.json()['results']
            for lexEntry in r_json[0]['lexicalEntries']:
                if lexEntry['lexicalCategory'].lower() == cat:
                    entry['en'] = self.sort_english(lexEntry['entries'])
                    if len(entry['en']) != 0:
                        return True, entry
            return False, entry
        else:
            return False, entry

    def lookup_html(self, word):
        entry_json, status_code = self.lookup_json(word)
        return DictEntry(json.loads(entry_json), status_code)

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

        if 'degree' in sorted[0].keys() and len(sorted) >= 1:
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


class DictEntry:
    def __init__(self, entry_json, status_code):
        self._json = entry_json
        self.category = entry_json['category']
        if self.category in ['noun', 'verb', 'adjective', 'unknown']:
            self.css_cat = self.category
        else:
            self.css_cat = 'other'
        self.de = entry_json['de']
        if status_code == 200:
            self.found = True
            self.root = entry_json['root']
            self.grammar_string = self.gen_grammar_string(entry_json['category'], entry_json['root'], entry_json['grammar'])
            self.en_string = self.gen_english_string(entry_json['en'])
        else:
            self.found = False
            self.grammar_string = "Unable to find {} in dictionary".format(self.de)

    @staticmethod
    def gen_english_string(english):
        en_string = ''
        for word in english:
            en_string = en_string + ', ' + word
        en_string = en_string[2:len(en_string)]
        return en_string

    @staticmethod
    def gen_grammar_string(category, root, grammar):
        if category == 'noun':
            return DictEntry.gen_noun_string(grammar[0], root)
        if category == 'verb':
            return DictEntry.gen_verb_string(grammar, root)
        if category == 'adjective':
            return DictEntry.gen_adjective_string(grammar[0], root)
        else:
            return DictEntry.gen_others(grammar[0], root)

    @staticmethod
    def gen_others(grammar, root):
        grammar_string = ''
        for feature in grammar.keys():
            grammar_string = grammar_string + '{}: {}, '.format(feature.capitalize(), grammar[feature])
        grammar_string = grammar_string + 'Root: <i>{}</i>.'.format(root)
        return grammar_string

    @staticmethod
    def gen_adjective_string(grammar, root):
        if grammar['degree'] == 'positive':
            return "Positive form."
        else:
            grammar_string = '{} form of <i>{}</i>.'.format(grammar['degree'], root)
            return grammar_string.capitalize()

    @staticmethod
    def gen_noun_string(grammar, root):
        if grammar['number'] == 'singular':
            return "Singular, {}".format(grammar['gender'].lower())
        else:
            return "Plural form of: <i>{}</i>".format(root)

    @staticmethod
    def gen_verb_string(grammar, root):
        if grammar[0]['tense'] == 'present':
            grammar_string = ''
            for g_form in grammar:
                grammar_string = grammar_string + ', {} person {}'.format(g_form['person'], g_form['number'])
            grammar_string = grammar_string[2:len(grammar_string)] + ' form of <i>{}</i>.'.format(root)
            return grammar_string.capitalize()
        elif grammar[0]['tense'] == 'past' and 'person' not in grammar[0].keys():
            grammar_string = "Perfect form of <i>{}</i>.".format(root)
            return grammar_string
        else:
            grammar_string = 'Past tense; '
            for g_form in grammar:
                grammar_string = grammar_string + '{} person {}, '.format(g_form['person'], g_form['number'])
            grammar_string = grammar_string[0:len(grammar_string) - 2] + ' form of <i>{}</i>.'.format(root)
            return grammar_string.capitalize()
