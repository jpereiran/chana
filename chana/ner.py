#coding=UTF-8
"""
Named-entity recognizer for shipibo-konibo
General functions to use the NER for shipibo-konibo.

Source model for the shipibo NER is from the Chana project
"""
import codecs
import collections
import re
import string
import numpy as np
import pycrfsuite


def load_array(file,array):
    f = codecs.open(file, "r", encoding= "utf-8")
    f_read = f.read()
    lines = f_read.splitlines()
    for word in lines:
        first_letter = word[0]
        array[first_letter].append(word)
    f.close()
    for key, elem in array.items():
        array[key]='|'.join(elem)

def is_number(word):
    numbers=['westiora','rabé','kimisha','chosko','pichika','sokota','kanchis','posaka','iskon','chonka','pacha','waranka']
    if word.lower() in numbers:
        return 'NUM'
    else
        return False

def is_location(word):
    pattern = re.compile('ain|nko|ainko|mea|meax|nkonia|nkoniax|kea|keax|ainoa|ainoax|oa|oax')
    
    letters = string.ascii_uppercase + 'Ñ'
    locations = dict.fromkeys(letters, [])
    
    load_array('files/CRF/per_esp_s.txt', locations)

    if word.istitle():
        first_letter = word[0]
        if pattern.search(word):
            return 'LOC'
        elif re.search('[ÑA-Z]', first_letter)!=None and re.compile(locations[first_letter]).search(word):
            return 'LOC'
    else:
        return False

def is_person(word):
    letters = string.ascii_uppercase + 'Ñ'
    names = dict.fromkeys(letters, [])
    
    load_array('files/CRF/per_esp_s.txt', names)

    if word.title():
        first_letter=word[0]
        if re.search('[ÑA-Z]', first_letter)!=None and re.compile(names[first_letter]).search(word):
            return 'PER'
    else:
        return False

def is_organization(word):
    letters = string.ascii_uppercase + 'Ñ'
    organizations = dict.fromkeys(letters, [])
    
    load_array('files/CRF/per_esp_s.txt', organizations)

    if word.title():
        first_letter=word[0]
        if re.search('[ÑA-Z]', first_letter)!=None and re.compile(organizations[first_letter]).search(word):
            return 'ORG'
    else:
        return False

def verificaFechas(word):
    months=['enero','febrero','marzo','abril','mayo','junio','julio','agosto','setiembre','octubre','noviembre','diciembre']
    if word.lower() in months:
        return 'FEC'


class ShipiboNER:
    """
    Instance of the rule based NER for shipibo
    """

    def __init__(self):
        self.letters = string.ascii_uppercase + 'Ñ'
        
        self.names = dict.fromkeys(letters, [])
        self.locations = dict.fromkeys(letters, [])
        self.organizations = dict.fromkeys(letters, [])

        self.tagger = pycrfsuite.Tagger()
        self.tagger.open('files/ner/crf_ner.crfsuite')


        load_array('files/ner/per_esp_s.dat',self.names)
        load_array('files/ner/loc_esp_s.dat',self.locations)
        load_array('files/ner/org_esp_s.dat',self.organizations)


    def load_array(file,array):
        f = codecs.open(file, "r", encoding= "utf-8")
        f_read = f.read()
        lines = f_read.splitlines()
        for word in lines:
            first_letter = word[0]
            array[first_letter].append(word)
        f.close()
        for key, elem in array.items():
            array[key]='|'.join(elem)


    def check_locations(words,entityTag):
        #sufijos locaciones
        pattern = re.compile('ain|nko|ainko|mea|meax|nkonia|nkoniax|kea|keax|ainoa|ainoax|oa|oax')
        idWord=0
        last_Loc=-1
        for word in words:
            if word.istitle():
                first_letter=word[0]
                if pattern.search(word):
                    entityTag[idWord]='LOC'
                    last_Loc=idWord
                elif re.search('[ÑA-Z]', first_letter)!=None and re.compile(self.locations[first_letter]).search(word):
                        entityTag[idWord]='LOC'
                        last_Loc=idWord
            idWord+=1

    def check_names(words,entityTag):
        idWord=0
        last_per=-1
        for word in words:
            if word.title():
                first_letter=word[0]
                if re.search('[ÑA-Z]', first_letter)!=None and re.compile(self.names[first_letter]).search(word):
                    entityTag[idWord]='PER'
                    last_per=idWord
            idWord+=1


    def check_organizations(words,entityTag):
        idWord=0
        last_org=-1
        for word in words:
            if word.title():
                first_letter=word[0]
                if re.search('[ÑA-Z]', first_letter)!=None and re.compile(self.organizations[first_letter]).search(word):
                    entityTag[idWord]='ORG'
                    last_org=idWord
            idWord+=1

    def check_numbers(words,entityTag):
        numbers=['westiora','rabé','kimisha','chosko','pichika','sokota','kanchis','posaka','iskon','chonka','pacha','waranka']
        idWord=0
        for word in words:
            if word.lower() in numbers:
                entityTag[idWord]='NUM'
            idWord+=1

    def check_dates(words,entityTag):
        months=['enero','febrero','marzo','abril','mayo','junio','julio','agosto','setiembre','octubre','noviembre','diciembre']
        idWord=0
        last_date=-1
        for word in words:
            if word.lower() in months:
                entityTag[idWord]='FEC'
                last_date=idWord
                if i > 0:
                    pre=words[idWord-1]
                    if pre.isdigit():
                        entityTag[idWord-1]='FEC'
                if i<len(words)-1:
                    pos=words[idWord+1]
                    if pos.isdigit():
                        entityTag[idWord+1]='FEC'
            idWord+=1

    def rule_tag(sentence):
        words=sentence.split()
        entityTag=[]
        for x in range(len(words)):
            entityTag.append('O')
        check_names(words,entityTag)
        check_organizations(words,entityTag)
        check_locations(words,entityTag)
        check_numbers(words,entityTag)
        check_dates(words,entityTag)
        return entityTag


    def word2features(sent, i):
        word = sent[i][0]
        tagBR = sent[i][1]
        features = [
            'bias',
            'word.lower=' + word.lower(),
            'word[-3:]=' + word[-3:],
            'word[-2:]=' + word[-2:],
            'word.isupper=%s' % word.isupper(),
            'word.istitle=%s' % word.istitle(),
            'word.isdigit=%s' % word.isdigit(),
            'tagBR=' + tagBR,
            'tagBR[:2]=' + tagBR[:2],
        ]
        if i > 0:
            word1 = sent[i-1][0]
            tagBR1 = sent[i-1][1]
            features.extend([
                '-1:word.lower=' + word1.lower(),
                '-1:word.istitle=%s' % word1.istitle(),
                '-1:word.isupper=%s' % word1.isupper(),
                '-1:tagBR=' + tagBR1,
                '-1:tagBR[:2]=' + tagBR1[:2],
            ])
        else:
            features.append('BOS')


        if i < len(sent)-1:
            word1 = sent[i+1][0]
            tagBR1 = sent[i+1][1]
            features.extend([
                '+1:word.lower=' + word1.lower(),
                '+1:word.istitle=%s' % word1.istitle(),
                '+1:word.isupper=%s' % word1.isupper(),
                '+1:tagBR=' + tagBR1,
                '+1:tagBR[:2]=' + tagBR1[:2],
            ])
        else:
            features.append('EOS')

        return features


    def sent2features(sent):
        return [word2features(sent, i) for i in range(len(sent))]



    def tag(sentence):
        entityTagBR=self.rule_tag(sentence)
        vectorWord=[]
        words=sentence.split()
        idWord=0
        for word in words:
                tag_BR=entityTagBR[idWord]
                etiqueta=(word,tag_BR)
                vectorWord.append(etiqueta)
                idWord+=1
        entityTag=self.tagger.tag(sent2features(vectorWord))
        return entityTag
