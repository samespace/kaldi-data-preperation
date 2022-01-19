import codecs

from phonetics import _normalize, IPA_normalization

#
# Lexicon load/save abstraction
#

class Lexicon(object):

    def __init__(self, file_path):
        """Load a lexicon
        :param file_path: E.g. dict-de.ipa or dict-en.ipa.
        """

        self.file_path  = file_path
        self.dictionary = {}
        self.multidict  = {}

        with open(self.file_path, 'r') as f:

            while True:

                line = f.readline().rstrip()

                if not line:
                    break

                parts = line.split(';')
                # print repr(parts)

                ipas = _normalize (parts[1],  IPA_normalization)

                k = parts[0]
                v = {'ipa': ipas}

                self.dictionary[k] = v
                b = k.split('_')[0]
                if not b in self.multidict:
                    self.multidict[b] = {}
                self.multidict[b][k] = v


    def __len__(self):
        return len(self.dictionary)

    def __getitem__(self, key):
        return self.dictionary[key]

    def __iter__(self):
        return iter(sorted(self.dictionary))

    def __setitem__(self, k, v):
        self.dictionary[k] = v
        b = k.split('_')[0]
        if not b in self.multidict:
            self.multidict[b] = {}
        self.multidict[b][k] = v

    def __contains__(self, key):
        return key in self.dictionary

    def get_multi(self, k):
        b = k.split('_')[0]
        return self.multidict[b]

    def save(self):
        with codecs.open(self.file_path, 'w', 'utf8') as f:
            for w in sorted(self.dictionary):
                entry = self.dictionary[w]
                f.write(u"%s;%s\n" % (w, entry['ipa']))

    def remove(self, key):
        del self.dictionary[key]