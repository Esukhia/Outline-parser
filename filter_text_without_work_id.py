import yaml
import re
import logging
from pathlib import Path
from fuzzy_match import algorithims

logging.basicConfig(filename="filter.log", level=logging.DEBUG, filemode="w")

def to_yaml(dict_):
    return yaml.safe_dump(dict_, sort_keys = False, allow_unicode=True)

def from_yaml(yml_path):
    return yaml.safe_load(yml_path.read_text(encoding='utf-8'))


def get_text_without_work_id(index):
    text_without_work_id = {}
    for uuid, text in index.items():
        if text['work_id'] == '':
            text_without_work_id[uuid] = text
    return text_without_work_id

def get_similarity(text1, text2):
    similarity = algorithims.cosine(text1,text2)
    return similarity

def get_text_sample(text, base_text):
    end = text['span'][0]['end']
    start = start = text['span'][0]['start']
    if re.search('རྒྱ་གར་སྐད་དུ', base_text[start:end]):
        start += re.search('རྒྱ་གར་སྐད་དུ', base_text[start:end]).start()
    if end-start > 2000:
        end = start + 2000
    sample_text = base_text[start:end]
    return sample_text


def get_match_text(derge_index, text_id):
    cur_text = {}
    for uuid, text in derge_index.items():
        if text['work_id'] == text_id:
            cur_text[uuid] = text
    return cur_text


def remove_target_durchen(text):
    try:
        start_pat = re.search('བསྡུར་མཆན', text).start()
        body_text = text[:start_pat]
        return body_text
    except:
        return text


def clean_text(text):
    text = re.sub('[^\u0F00-\u0FFF]', '', text)
    text = text.replace('\n', '')
    return text 


def match_text(target_text, derge_texts):
    for uuid, text in derge_texts.items():
        cur_base_text = Path(f"./P000002.opf/base/v{int(text['span'][0]['vol']):03}.txt").read_text(encoding = 'utf-8')
        cur_text_sample = get_text_sample(text, cur_base_text)
        clean_target_text = clean_text(target_text)
        clean_target_text = remove_target_durchen(clean_target_text)
        clean_text_sample = clean_text(cur_text_sample)
        if len(clean_target_text)> len(clean_text_sample) and re.search('རྒྱ་གར་སྐད་དུ', clean_target_text):
            clean_target_text = clean_target_text[:len(clean_text_sample)]
        similarity = get_similarity(clean_target_text, clean_text_sample)
        if similarity > 0.80:
            return (text['work_id'], similarity)
    return ('', 0)


def get_max_match(cur_matches):
    max_match = [cur_matches[0][0], cur_matches[0][1]]
    for derge_text_id, similarity in cur_matches:
        if similarity > max_match[1]:
            max_match = [derge_text_id, similarity]
    return max_match

def fix_text_without_work_id(target_index_file, derge_index, text_not_in_target):
    target_index = target_index_file['annotations']
    text_without_work_id = get_text_without_work_id(target_index)
    prev_vol = 0
    for uuid, target_text in text_without_work_id.items():
        cur_matches = []
        if prev_vol != target_text['span'][0]['vol']:
                cur_base_text = Path(f"./P000009.opf/base/v{int(target_text['span'][0]['vol']):03}.txt").read_text(encoding = 'utf-8')
                prev_vol = target_text['span'][0]['vol']
        target_text_sample = get_text_sample(target_text, cur_base_text)
        for derge_text in text_not_in_target:
            derge_texts = get_match_text(derge_index, derge_text)
            derge_text_id, similarity = match_text(target_text_sample, derge_texts)
            if derge_text_id:
                cur_matches.append((derge_text_id, similarity))
        if cur_matches:
            max_match = get_max_match(cur_matches)
            logging.info(f"{uuid} is matched with {max_match[0]} having similarity of {max_match[1]*100}%")
        if not cur_matches:
            logging.info(f"{uuid} not matched with anything..")

if __name__ == "__main__":
    target_index_file = from_yaml(Path(f"./new_index/pedurma_index.yml"))
    derge_index_file = from_yaml(Path(f"./P000002.opf/index.yml"))
    derge_index = derge_index_file['annotations']
    text_not_in_target = Path('./text_not_in_pedurma.txt').read_text(encoding='utf-8').splitlines()
    fix_text_without_work_id(target_index_file, derge_index, text_not_in_target)
    

