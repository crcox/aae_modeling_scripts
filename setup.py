#!/usr/bin/env python

import os,json,pickle,sys
import sqlite3
from aae import parse,sample,rules,dialects,semantics

try:
    stimoptspath = sys.argv[1]
except:
    stimoptspath = "stimopts.json"

with open(stimoptspath,'r') as f:
    jdat = json.load(f)

# Load the corpus
PHON_MAP = getattr(dialects, jdat['phon_map'])
SEM_MAP  = getattr(semantics, jdat['sem_map'])
CORPUS = parse.corpus(jdat['stim_master'], SEM_MAP, PHON_MAP, jdat['phon_map'], 'SAE')

# Create AAE
AAE_RULES = ['consonant_cluster_reduction', 'postvocalic_reduction']
CORPUS,changelog = parse.altpronunciation(CORPUS, 'AAE', AAE_RULES, PHON_MAP)

# Populate database with this corpus wrt the dialect specified in PHON_MAP.
# Tables need to be set up one at a time. Each ``with'' block contains a
# transaction with a particular table. The ``with'' convention will ensure that
# the changes are committed, even if the block does not complete. This may not
# be what we want, ultimately. Learning as I go...
words = [(w,CORPUS[w]['orth_code']) for w in CORPUS.keys()]
conn = sqlite3.connect('aae.db')
conn.row_factory = sqlite3.Row

#
# Corpora
#
cmd_insert = "INSERT INTO corpora (label, description) VALUES (:label,:desc)"
corpus='3k'
description='There should be something informative here.'
with conn:
    cur = conn.cursor()
    cur.execute(cmd_insert, {'label': corpus, 'desc': description})

#
# Dialects
#
cmd_insert = "INSERT INTO dialects (label, description) VALUES (:label,:desc)"
dialect = 'standard'
description = 'There should be something informative here.'
with conn:
    cur = conn.cursor()
    cur.execute(cmd_insert, {'label': dialect, 'desc': description})

#
# Languages
#
languages = [
    ('SAE' , 'Standard American English') ,
    ('AAE' , 'African American English')
]
cmd_insert = "INSERT INTO languages (label, description) VALUES (:label,:desc)"
with conn:
    cur = conn.cursor()
    for row in languages:
        cur.execute(cmd_insert, {'label': row[0], 'desc': row[1]})

#
# Rules
#
rules = [
    ('devoice'                     , 'There should be something informative here.') ,
    ('consonant_cluster_reduction' , 'There should be something informative here.') ,
    ('postvocalic_reduction'       , 'There should be something informative here.')
]
cmd_insert = "INSERT INTO rules (label, description) VALUES (:label,:desc)"
with conn:
    cur = conn.cursor()
    for row in rules:
        cur.execute(cmd_insert, {'label': row[0], 'desc': row[1]})

#
# Phonemes
# references: dialects
#
cmd_insert = "INSERT INTO phonemes (phoneme) VALUES (:phoneme)"
with conn:
    cur = conn.cursor()
    for phoneme in PHON_MAP.keys():
        cur.execute(cmd_insert, {'phoneme': phoneme})
#
# Words
# references: corpora
#
cmd_insert = "INSERT INTO words (corpus_id,word,orthography) VALUES (:corpus_id,:word,:orth)"
with conn:
    cur = conn.cursor()
    cmd_select = "SELECT id FROM corpora WHERE label=:corpus LIMIT 1"
    cur.execute(cmd_select, {'corpus': corpus})
    r = cur.fetchone()
    corpus_id = r['id']
    for row in words:
        cur.execute(cmd_insert, {'corpus_id':corpus_id, 'word': row[0], 'orth': row[1]})

#
# Language Definitions (mapping from languages to rules)
# references: languages, rules
#
AAE_RULES = ['consonant_cluster_reduction', 'postvocalic_reduction']
langdef = {'AAE': AAE_RULES, 'SAE': []}
cmd_insert = "INSERT INTO langdefs (language_id,rule_id) VALUES (:lid,:rid)"
with conn:
    cur = conn.cursor()
    for lang,definition in langdef.items():
        for rule in definition:
            cmd_select = "SELECT id FROM languages WHERE label=:lang LIMIT 1"
            cur.execute(cmd_select, {'lang': lang})
            r = cur.fetchone()
            language_id = r['id']

            cmd_select = "SELECT id FROM rules WHERE label=:rule LIMIT 1"
            cur.execute(cmd_select, {'rule': rule})
            r = cur.fetchone()
            rule_id = r['id']

            cur.execute(cmd_insert, {'lid': language_id, 'rid': rule_id})

#
# Phonology
# references: words, languages
#
cmd_insert = "INSERT INTO phonology (word_id,language_id,phoncode) VALUES (:wid,:lid,:phon)"
with conn:
    cur = conn.cursor()
    for lang in ['SAE','AAE']:
        phon = [(w,CORPUS[w]['phon_code'][lang]) for w in CORPUS.keys()]
        for row in phon:
            word = row[0]
            phon = row[1]
            cur.execute("SELECT id FROM words WHERE word='{w:s}' LIMIT 1".format(w=word))
            r = cur.fetchone()
            word_id = r['id']
            cur.execute("SELECT id FROM languages WHERE label='{l:s}' LIMIT 1".format(l=lang))
            r = cur.fetchone()
            language_id = r['id']
            cur.execute(cmd_insert, {'wid': word_id, 'lid': language_id, 'phon': phon})

#
# Rule Application (mapping from phoncodes to rules)
# references: rules, phonology, words, languages
#
lang = 'AAE'
cmd_insert = "INSERT INTO ruleapplication (rule_id,phon_id) VALUES (:rid,:pid)"
with conn:
    cur = conn.cursor()
    for rule,affectedwords in changelog.items():
        cmd_select = "SELECT id FROM rules WHERE label=:rule LIMIT 1"
        cur.execute(cmd_select, {'rule': rule})
        r = cur.fetchone()
        rule_id = r['id']
        for word in affectedwords:
            cmd_select = (
                "SELECT a.id as id, a.phoncode as phoncode, b.word as word, c.label as language "
                "FROM phonology a "
                "LEFT OUTER JOIN words b ON a.word_id=b.id "
                "LEFT OUTER JOIN languages c on a.language_id=c.id "
                "WHERE word=:word "
                "AND language=:lang"
            )
            cur.execute(cmd_select, {'word':word, 'lang':lang})
            r = cur.fetchone()
            phon_id = r['id']

            cur.execute(cmd_insert, {'rid': rule_id, 'pid': phon_id})



#
# PhonMap (map phoncodes to constituent phonemes)
# references: phonemes, phonology, words, languages
#
cmd_insert = "INSERT INTO phonmap (phon_id,phoneme_id,unit) VALUES (:phon_id,:phoneme_id,:unit)"
with conn:
    cur = conn.cursor()
    for lang in ['SAE','AAE']:
        phon = [(w,CORPUS[w]['phon_code'][lang]) for w in CORPUS.keys()]
        for row in words:
            word = row[0]
            phon = row[1]
            cmd_select = (
                "SELECT a.id as id, a.phoncode as phoncode, b.word as word, c.label as language "
                "FROM phonology a "
                "LEFT OUTER JOIN words b ON a.word_id=b.id "
                "LEFT OUTER JOIN languages c on a.language_id=c.id "
                "WHERE word=:word "
                "AND language=:lang"
            )
            cur.execute(cmd_select, {'word':word, 'lang':lang})
            r = cur.fetchone()
            phon_id = r['id']
            phoncode = r['phoncode']
            for i,p in enumerate(phoncode):
                cmd_select = "SELECT id FROM phonemes WHERE phoneme=:phoneme"
                cur.execute(cmd_select, {'phoneme':p})
                r = cur.fetchone()
                phoneme_id = r['id']
                cur.execute(cmd_insert, {'phon_id': phon_id, 'phoneme_id': phoneme_id, 'unit': i})

#
# PhonRep (map phonemes to binary code, by dialect)
# references: 
#
dialect = jdat['phon_map']
cmd_insert = "INSERT INTO phonrep (phoneme_id,dialect_id,unit,value) VALUES (:phoneme_id,:dialect_id,:unit,:value)"
with conn:
    cur = conn.cursor()
    cmd_select = "SELECT id FROM dialects WHERE label=:dialect LIMIT 1"
    cur.execute(cmd_select, {'dialect': dialect})
    r = cur.fetchone()
    dialect_id = r['id']
    for phoneme,representation in PHON_MAP.items():
        cmd_select = "SELECT id FROM phonemes WHERE phoneme=:phoneme LIMIT 1"
        cur.execute(cmd_select, {'phoneme': phoneme})
        r = cur.fetchone()
        phoneme_id = r['id']
        for i,value in enumerate(representation):
            cur.execute(cmd_insert, {'phoneme_id':phoneme_id, 'dialect_id': dialect_id, 'unit': i, 'value': value})

#
# SemRep (map words to binary code, by corpus)
# references: 
#
corpus = '3k'
cmd_insert = "INSERT INTO semrep (word_id,corpus_id,unit,value) VALUES (:word_id,:corpus_id,:unit,:value)"
with conn:
    cur = conn.cursor()
    cmd_select = "SELECT id FROM corpora WHERE label=:corpus LIMIT 1"
    cur.execute(cmd_select, {'corpus': corpus})
    r = cur.fetchone()
    corpus_id = r['id']
    for word,representation in SEM_MAP.items():
        cmd_select = "SELECT id FROM words WHERE word=:word AND corpus_id=:corpus_id LIMIT 1"
        cur.execute(cmd_select, {'word': word, 'corpus_id': corpus_id})
        r = cur.fetchone()
        word_id = r['id']
        for i,value in enumerate(representation):
            cur.execute(cmd_insert, {'word_id':word_id, 'corpus_id': corpus_id, 'unit': i, 'value': value})

conn.close()
#for k,v in changelog.items():
#    print "{k:s}: {n:d}".format(k=k, n=len(v))

#subcorpus,subhomo = sample.subcorpus(CORPUS,500, 250, 20)
#subcorpus,changelog = parse.altpronunciation(subcorpus, 'AAE', AAE_RULES, PHON_MAP)
#
#for k,v in changelog.items():
#    print "{k:s}: {n:d}".format(k=k, n=len(v))
#
#print "AAE homo: {n}".format(n=len(subhomo['AAE']))
#print "SAE homo: {n}".format(n=len(subhomo['SAE']))



#root = os.path.join('stimuli','SAE')
#ppath = os.path.join(root,'pkl','words_master.pkl')
#with open(ppath,'wb') as f:
#    pickle.dump(STIM,f)
#
#jpath = os.path.join(root,'json','words_master.json')
#with open(jpath,'wb') as f:
#    json.dump(STIM,f,indent=2, separators=(',', ': '))
#
#ppath = os.path.join(root,'pkl','homo_master.pkl')
#with open(ppath,'wb') as f:
#    pickle.dump(HOMO,f)
#
#jpath = os.path.join(root,'json','homo_master.json')
#with open(jpath,'wb') as f:
#    json.dump(HOMO,f,indent=2, separators=(',', ': '))
