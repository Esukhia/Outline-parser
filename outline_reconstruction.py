import re
import yaml
import logging

from bs4 import BeautifulSoup
from collections import defaultdict
from pathlib import Path
from pyewts import pyewts
from fuzzy_match import algorithims
from uuid import uuid4

converter = pyewts()

def to_yaml(dict_):
    return yaml.safe_dump(dict_, sort_keys = False, allow_unicode=True)

def from_yaml(yml_path):
    return yaml.safe_load(yml_path.read_text(encoding='utf-8'))

def preprocess_title(title):
    initials = ['དཔལ་', 'འཕགས་པ་']
    for initial in initials:
        title = title.replace(initial, '')
    return title

def restructure_outline(text_durchen, ab_titles):
    texts = []
    prev_title = "ཁྱད་པར་དུ་འཕགས་པའི་བསྟོད་པ།" 
    prev_vol = "0"
    cur_text = []
    for text_id, text in text_durchen.items():
        if text['title'] == prev_title:
            if text['title'] not in ab_titles:
                cur_text.append((text_id,text))
            else:
                texts.append(cur_text)
                cur_text = []
                cur_text.append((text_id,text)) 
        else:
            texts.append(cur_text)
            cur_text = []
            cur_text.append((text_id,text))
        prev_title = text["title"]
        prev_vol = text["vol"]
    if cur_text:
        texts.append(cur_text)
    return texts

def get_similarity(title1, title2):
    similarity = algorithims.levenshtein(title1,title2)
    return similarity

def get_text_from_rkts(title, rkts_info):
    for index, text in enumerate(rkts_info):
        title1 = preprocess_title(title)
        title2 = preprocess_title(text[2])
        similarity = get_similarity(title1, title2)
        if similarity >= 0.97:
            match_text = text
            del rkts_info[index]
            return (match_text, rkts_info)
    return ([], rkts_info)

def reconstruct_text(text_id, text, title):
    print(text_id)
    if title:
        cur_text[text_id] = {
            'pedurma_title': text['title'],
            'text_title': title[2],
            'rkts_id': title[1],
            'type': text['type'],
            'img_loc_start': text['img_loc_start'],
            'img_loc_end': text['img_loc_end'],
            'pg_start': text['pg_start'],
            'pg_end': text['pg_end'],
            'vol': text['vol'],
            'durchen': text['durchen'],    
        }
    else:
        cur_text[text_id] = {
            'pedurma_title': text['title'],
            'text_title': '',
            'rkts_id': '',
            'type': text['type'],
            'img_loc_start': text['img_loc_start'],
            'img_loc_end': text['img_loc_end'],
            'pg_start': text['pg_start'],
            'pg_end': text['pg_end'],
            'vol': text['vol'],
            'durchen': text['durchen'],    
        }
        
    return cur_text

def get_abnormal_titles(tegyur_pedurma_text_title):
    i = 1
    ab_title = []
    for (r_id, t_id, title) in tegyur_pedurma_text_title[1:]:
        prev_title = tegyur_pedurma_text_title[i-1][2]
        if title == prev_title and i != 1:
            ab_title.append(title)
        i+=1
    return set(ab_title)

def get_new_outline(old_outline, text_titles):
    ab_titles = get_abnormal_titles(text_titles)
    textwise_outline = restructure_outline(old_outline, ab_titles)
    new_outline = {}
    for text in textwise_outline:
        text_title = text[0][1]['title']
        match_text, text_titles = get_text_from_rkts(text_title, text_titles)
        for text_part in text:
            cur_text = {}
            cur_text = reconstruct_text(text_part[0], text_part[1], match_text)
            new_outline.update(cur_text)
    print(f"number of unallocated text {len(text_titles)}\n")
    return new_outline