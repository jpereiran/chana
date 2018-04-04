#coding=UTF-8
"""
Named-entity recognizer for shipibo-konibo
General functions to use the NER for shipibo-konibo or to train a new one for other languages.

Source model for the shipibo NER is from the Chana project
"""
import codecs
import collections
import re
import string
import numpy as np
import pycrfsuite


def is_number(word):
    numbers=['westiora','rabé','kimisha','chosko','pichika','sokota','kanchis','posaka','iskon','chonka','pacha','waranka']
    if word.lower() in numbers:
        return 'NUM'
    else
        return False


def is_location(word):
    pattern = re.compile('ain|nko|ainko|mea|meax|nkonia|nkoniax|kea|keax|ainoa|ainoax|oa|oax')
    idWord=0
    ultimaLoc=-1
    for palabra in palabras:
        if palabra.istitle():
            inicial=palabra[0]
            if pattern.search(palabra):
                entityTag[idWord]='LOC'
                ultimaLoc=idWord
            elif re.search('[ÑA-Z]', inicial)!=None and re.compile(locaciones[inicial]).search(palabra):
                    entityTag[idWord]='LOC'
                    ultimaLoc=idWord
        idWord+=1



def is_person(palabras,entityTag):
    idWord=0
    ultimaPer=-1
    for palabra in palabras:
        if palabra.title():
            inicial=palabra[0]
            if re.search('[ÑA-Z]', inicial)!=None and re.compile(personas[inicial]).search(palabra):
                entityTag[idWord]='PER'
                ultimaPer=idWord
        idWord+=1


def is_organization(palabras,entityTag):
    idWord=0
    ultimaOrg=-1
    for palabra in palabras:
        if palabra.title():
            inicial=palabra[0]
            if re.search('[ÑA-Z]', inicial)!=None and re.compile(organizaciones[inicial]).search(palabra):
                entityTag[idWord]='ORG'
                ultimaOrg=idWord
        idWord+=1

def verificaFechas(palabras,entityTag):
    meses=['enero','febrero','marzo','abril','mayo','junio','julio','agosto','setiembre','octubre','noviembre','diciembre']
    idWord=0
    ultimaFec=-1
    for palabra in palabras:
        if palabra.lower() in meses:
            entityTag[idWord]='FEC'
            ultimaFec=idWord
            if i > 0:
                pre=palabras[idWord-1]
                if pre.isdigit():
                    entityTag[idWord-1]='FEC'
            if i<len(palabras)-1:
                pos=palabras[idWord+1]
                #14 abril 2014
                if pos.isdigit():
                    entityTag[idWord+1]='FEC'
        idWord+=1






class ShipiboRuleNER:
    """
    Instance of the rule based NER for shipibo
    """

    def __init__(self):
        self.letters = string.ascii_uppercase + 'Ñ'
        
        self.names = dict.fromkeys(letters, [])
        self.locations = dict.fromkeys(letters, [])
        self.organizations = dict.fromkeys(letters, [])

        load_array('files/CRF/per_esp_s.txt',self.names)
        load_array('files/CRF/loc_esp_s.txt',self.locations)
        load_array('files/CRF/org_esp_s.txt',self.organizations)


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



    def verificaLocaciones(palabras,entityTag):
        #sufijos locaciones
        pattern = re.compile('ain|nko|ainko|mea|meax|nkonia|nkoniax|kea|keax|ainoa|ainoax|oa|oax')
        idWord=0
        ultimaLoc=-1
        for palabra in palabras:
            if palabra.istitle():
                inicial=palabra[0]
                if pattern.search(palabra):
                    entityTag[idWord]='LOC'
                    ultimaLoc=idWord
                elif re.search('[ÑA-Z]', inicial)!=None and re.compile(locaciones[inicial]).search(palabra):
                        entityTag[idWord]='LOC'
                        ultimaLoc=idWord
            idWord+=1

    def verificarPersonas(palabras,entityTag):
        idWord=0
        ultimaPer=-1
        for palabra in palabras:
            if palabra.title():
                inicial=palabra[0]
                if re.search('[ÑA-Z]', inicial)!=None and re.compile(personas[inicial]).search(palabra):
                    entityTag[idWord]='PER'
                    ultimaPer=idWord
            idWord+=1


    def verificarOrganizaciones(palabras,entityTag):
        idWord=0
        ultimaOrg=-1
        for palabra in palabras:
            if palabra.title():
                inicial=palabra[0]
                if re.search('[ÑA-Z]', inicial)!=None and re.compile(organizaciones[inicial]).search(palabra):
                    entityTag[idWord]='ORG'
                    ultimaOrg=idWord
            idWord+=1

    def verificaNumeros(palabras,entityTag):
        numeros=['westiora','rabé','kimisha','chosko','pichika','sokota','kanchis','posaka','iskon','chonka','pacha','waranka']
        idWord=0
        ultimoNum=-1
        for palabra in palabras:
            if palabra.lower() in numeros:
                entityTag[idWord]='NUM'
                ultimoNum=idWord
            idWord+=1


    def verificaFechas(palabras,entityTag):
        meses=['enero','febrero','marzo','abril','mayo','junio','julio','agosto','setiembre','octubre','noviembre','diciembre']
        idWord=0
        ultimaFec=-1
        for palabra in palabras:
            if palabra.lower() in meses:
                entityTag[idWord]='FEC'
                ultimaFec=idWord
                if i > 0:
                    pre=palabras[idWord-1]
                    if pre.isdigit():
                        entityTag[idWord-1]='FEC'
                if i<len(palabras)-1:
                    pos=palabras[idWord+1]
                    #14 abril 2014
                    if pos.isdigit():
                        entityTag[idWord+1]='FEC'
            idWord+=1


    def basadoEnReglas(oracion):
        palabras=oracion.split()
        entityTag=[]
        for x in range(len(palabras)):
            entityTag.append('O')
        verificarPersonas(palabras,entityTag)
        verificarOrganizaciones(palabras,entityTag)
        verificaLocaciones(palabras,entityTag)
        verificaNumeros(palabras,entityTag)
        verificaFechas(palabras,entityTag)
        return entityTag






#Modelo basado en caracteristicas

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






@app.route('/chaner/api/ner/<string:sentence>', methods=['GET'])
def ner(sentence):
        entityTagBR=basadoEnReglas(sentence)
        vectorWord=[]
        words=sentence.split()
        idWord=0
        for word in words:
                tag_BR=entityTagBR[idWord]
                etiqueta=(word,tag_BR)
                vectorWord.append(etiqueta)
                idWord+=1
        entityTag=tagger.tag(sent2features(vectorWord))
        return jsonify({'result':entityTag})
