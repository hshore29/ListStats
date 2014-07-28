# Class object for text analysis using nltk
# Based on an implementation of flesch-kincaid found here:
# www.slumberheart.com/things/flesch_kincaid.py

import nltk, datetime
from nltk.corpus import cmudict
from re import match

class FleschKincaid:
    def __init__(self,text):
        # Initialize vars
        self.sent_count = 0
        self.word_count = 0
        self.syll_count = 0
        self.cmu = cmudict.dict()
        self.processText(text)

    # Process text
    def processText(self,text):
        sentances = nltk.tokenize.sent_tokenize(text)
        self.sent_count = len(sentances)
        for sentance in sentances:
            words = nltk.tokenize.word_tokenize(sentance)
            words = [self.reduce(word) for word in words]
            words = [word for word in words if word != '']
            self.word_count += len(words)
            syllables = [self.syllable_count(word) for word in words]
            self.syll_count += sum(syllables)

    def reduce(self,word):
        return ''.join([x for x in word.lower() if match(r'\w', x)])

    def syllable_count(self,word):
        reduced = self.reduce(word)
        if (not len(reduced)) or (not reduced in self.cmu):
            return 0
        return len([x for x in list(''.join(list(self.cmu[reduced])[-1])) if match(r'\d', x)])

    def gradeLevel(self):
        if self.sent_count > 0 and self.word_count > 0:
            return (0.39 * (float(self.word_count) / self.sent_count)
                    + 11.8 * (float(self.syll_count) / self.word_count)
                    - 15.59)
        else:
            return 0

    def minAge(self):
        return int(round(self.gradeLevel() + 5))
