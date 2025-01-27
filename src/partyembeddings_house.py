#!/usr/bin/python3
# -*- coding: utf-8 -*-

#=====================================================================#
#
# Description:
# An example script to fit word embeddings with political metadata.
# For more information, see www.github.com/lrheault/partyembed
#
# Usage:
# python3 partyembeddings_house.py
#
# @author: L. Rheault
#          modified by C. Moore
#
#=====================================================================#

import gensim
from gensim.models.doc2vec import Doc2Vec
from gensim.models.phrases import Phrases, Phraser
from gensim import corpora
from collections import namedtuple
import logging

logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)
assert gensim.models.doc2vec.FAST_VERSION > -1

class corpusIterator(object):

    def __init__(self, inpath, house, bigram=None, trigram=None):
        if bigram:
            self.bigram = bigram
        else:
            self.bigram = None
        if trigram:
            self.trigram = trigram
        else:
            self.trigram = None
        self.house = house
        self.inpath = inpath

    def __iter__(self):
        self.speeches = namedtuple('speeches', 'words tags')
        with open(self.inpath, 'r', encoding='UTF-8') as f:
            for line in f:
                ls = line.split('\t')
                chamber = ls[5]
                if chamber==self.house:
                    text = ls[2].replace('\n','')
                    congress = str(ls[0])
                    party = ls[7]
                    member = ls[4]
                    MP_tag = member + '_' + party + '_' + congress
                    congresstag = 'CONGRESS_' + congress
                    tokens = text.split()
                    if self.bigram and self.trigram:
                        self.words = self.trigram[self.bigram[tokens]]
                    elif self.bigram and not self.trigram:
                        self.words = self.bigram[tokens]
                    else:
                        self.words = tokens
                    self.tags = [MP_tag, congresstag] # [partytag, congresstag]
                    yield self.speeches(self.words, self.tags)

class phraseIterator(object):

    def __init__(self, inpath, house):
        self.inpath = inpath
        self.house = house

    def __iter__(self):
        with open(self.inpath, 'r', encoding='UTF-8') as f:
            i=0
            for line in f:
                ls = line.split('\t')
                chamber = ls[5]
                if i==1: 
                    print(ls[5])
                    print('.........')
                    print(self.house)
                    print('.........')
                i += 1
                if chamber==self.house:
                    text = ls[2].replace('\n','')
                    yield text.split()

if __name__=='__main__':

    # Fill in the paths to desired location.
    # Corpus is expected to be in tab-separated format with column ordering specified in
    # reformat_congress.py, and clean text in column #10.

    inpath = 'src/38to42Parl_forembeddings.csv'
    savepath = 'partyembed/models/'

    phrases = Phrases(phraseIterator(inpath, house='HoC'))
    bigram = Phraser(phrases)
    tphrases = Phrases(bigram[phraseIterator(inpath, house='HoC')])
    trigram = Phraser(tphrases)

    # To save phraser objects for future usage.
    # bigram.save('.../phraser_bigrams')
    # trigram.save('.../phraser_trigrams')
    print('-----------')
    model0 = Doc2Vec(vector_size=200, window=20, min_count=50, workers=8, epochs=5)
    model0.build_vocab(corpusIterator(inpath, house='HoC', bigram=bigram, trigram=trigram))
    model0.train(corpusIterator(inpath, house='HoC', bigram=bigram, trigram=trigram), total_examples=model0.corpus_count, epochs=model0.epochs)
    model0.save(savepath + '38to42Parl')
