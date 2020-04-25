import io
import os # for final printout only
import re
import argparse
import pandas as pd

import zipfile
import os.path

import nltk
from nltk.corpus import stopwords 
nltk.download('stopwords')

def read_args():
    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument('-d', '--dict', type=str)
    arg_parser.add_argument('-i', '--fileindex', type=str)
    args = arg_parser.parse_args()        
    return (args.dict, args.fileindex)

# [1] load lexicon into memory
def load_lexicon(lexicon_path):
    file = io.open(lexicon_path, mode="r", encoding="latin-1")
    return { x.lower() : 0 for x in re.split('\n', file.read()) }

# [2] load ebook into memory 
def load_ebook(ebook_path):
    file = io.open(ebook_path, mode="r", encoding="latin-1")
    return file.read()

# [3] split ebook into a token list (separate by space and dash)
def tokenize_ebook(ebook_contents):
    token_list = re.split('\s+|-+', ebook_contents)
    return [x for x in token_list if x != '']


# [4] pre-process token:
#   * convert token to lower-case
#   * strip any non-letters from the start & end of the token
def pre_process(token):
    token = token.lower()
    token = re.sub("^[^a-z]+", "", token) 
    token = re.sub("[^a-z]+$", "", token)
    return token
        
# [5] TEST: is token a valid word?
#     DEFINITION: only contains a-z and apostrophes (')
#     EXTRA: must contain a vowel or y
def is_valid_word(token):
    if re.search("^[a-z\']+$", token):
        if re.search("[aeiouy]", token): return True
        else: return False
    else: return False

# [6] TEST: is token a stop word?
def is_stop_word(token):
    if token in stopwords.words('english'): return True
    else: return False

# [7] TEST: is token in lexicon?
def is_in_lexicon(token, lexicon):
    if token in lexicon.keys(): return True
    else: return False
    
# [8a] calulate the unique count and total frequency of tokens in a list
def calc_stats(tokenlist):
    df = pd.DataFrame(tokenlist, columns=['token']).groupby('token')
    token_count = len(df['token'].unique().tolist())
    token_frequency =  df.size().sum()
    return (token_count, token_frequency) 

# [8b] print out summary statstics
def print_stats(stats):
    print (os.linesep)
    print (f"[UNIQUE WORD COUNT]")
    print (f"TOTAL WORDS = {stats['cnt']['tot']}")
    print (f"IN LEXICON = {stats['cnt']['lex']} ({stats['cnt']['lex']*100/stats['cnt']['tot']:.2f}%)")
    print (f"NOT IN LEXICON = {stats['cnt']['notlex']} ({stats['cnt']['notlex']*100/stats['cnt']['tot']:.2f}%)")
    print (f"STOP WORDS = {stats['cnt']['stop']} ({stats['cnt']['stop']*100/stats['cnt']['tot']:.2f}%)")
    print (f"UNKNOWN (DISCARDS) ={stats['cnt']['disc']} ({stats['cnt']['disc']*100/stats['cnt']['tot']:.2f}%)")
    print (os.linesep)
    print (f"[TOTAL WORD COUNT (FREQUENCY)]")
    print (f"TOTAL WORDS = {stats['frq']['tot']}")
    print (f"IN LEXICON = {stats['frq']['lex']} ({stats['frq']['lex']*100/stats['frq']['tot']:.2f}%)")
    print (f"NOT IN LEXICON = {stats['frq']['notlex']} ({stats['frq']['notlex']*100/stats['frq']['tot']:.2f}%)")
    print (f"STOP WORDS = {stats['frq']['stop']} ({stats['frq']['stop']*100/stats['frq']['tot']:.2f}%)")
    print (f"UNKNOWN (DISCARDS) = {stats['frq']['disc']} ({stats['frq']['disc']*100/stats['frq']['tot']:.2f}%)")
    print (os.linesep)

###################################
### MAIN CODE LOGIC STARTS HERE ###
###################################

(lexicon, file_index) = read_args()
lexicon = load_lexicon(lexicon)

with open(file_index) as idx:
    file_list = idx.readlines()

# process all files in the file index
processed_files = 0
for f in file_list:
    fname = f.rstrip()
    ebook_contents = load_ebook(fname)
    ebook_tokens = tokenize_ebook(ebook_contents)

    word_lists = { 'discards' : [], 'stopwords' : [],
                   'in-lexicon' : [], 'not-in-lexicon' : [] }

    for token in ebook_tokens:
        token = pre_process(token)
        if not is_valid_word(token):
            word_lists['discards'].append(token)
        else:
            if is_stop_word(token):
                word_lists['stopwords'].append(token)
            elif is_in_lexicon(token, lexicon):
                word_lists['in-lexicon'].append(token)
            else:
                word_lists['not-in-lexicon'].append(token)

    (disc_cnt, disc_frq) = calc_stats(word_lists['discards'])
    (stop_cnt, stop_frq) = calc_stats(word_lists['stopwords'])
    (lex_cnt, lex_frq) = calc_stats(word_lists['in-lexicon'])
    (notlex_cnt, notlex_frq) = calc_stats(word_lists['not-in-lexicon'])

    stats = {
        'cnt' : { 'lex'     : lex_cnt,
                  'notlex'  : notlex_cnt,
                  'stop'    : stop_cnt,
                  'disc'    : disc_cnt },
        'frq' : { 'lex'     : lex_frq,
                  'notlex'  : notlex_frq,
                  'stop'    : stop_frq,
                  'disc'    : disc_frq }
    }
    stats['cnt']['tot'] = sum(stats['cnt'].values())
    stats['frq']['tot'] = sum(stats['frq'].values())

    score_c   = 100 * stats['cnt']['lex'] / (stats['cnt']['notlex'] + stats['cnt']['lex'])
    score_f    = 100 * stats['frq']['lex'] / (stats['frq']['notlex'] + stats['frq']['lex'])
    cover_c = 100 * (stats['cnt']['lex'] + stats['cnt']['notlex']) / (stats['cnt']['tot'] - stats['cnt']['stop'])
    cover_f = 100 * (stats['frq']['lex'] + stats['frq']['notlex']) / (stats['frq']['tot'] - stats['frq']['stop'])


    print_stats(stats)
    print (f"{score_c:.2f},{cover_c:.2f},{score_f:.2f},{cover_f:.2f},{ebook}")