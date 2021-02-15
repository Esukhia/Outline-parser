import yaml
import re
import logging
from pathlib import Path
from fuzzy_match import algorithims

logging.basicConfig(filename="cross_check.log", level=logging.DEBUG, filemode="w")

def get_similarity(text1, text2):
    similarity = algorithims.cosine(text1,text2)
    return similarity

def to_yaml(dict_):
    return yaml.safe_dump(dict_, sort_keys = False, allow_unicode=True)

def from_yaml(yml_path):
    return yaml.safe_load(yml_path.read_text(encoding='utf-8'))

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

def remove_pedurma_durchen(text):
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


def match_text(pedurma_text, derge_texts):
    for uuid, text in derge_texts.items():
        cur_base_text = Path(f"./P000002.opf/base/v{int(text['span'][0]['vol']):03}.txt").read_text(encoding = 'utf-8')
        cur_text_sample = get_text_sample(text, cur_base_text)
        clean_pedurma_text = remove_pedurma_durchen(pedurma_text)
        clean_pedurma_text = clean_text(clean_pedurma_text)
        clean_text_sample = clean_text(cur_text_sample)
        if len(clean_pedurma_text)> len(clean_text_sample) and re.search('རྒྱ་གར་སྐད་དུ', clean_pedurma_text):
            clean_pedurma_text = clean_pedurma_text[:len(clean_text_sample)]
        similarity = get_similarity(clean_pedurma_text, clean_text_sample)
        if similarity > 0.95:
            return uuid
    return ''


def get_leftover_text(index):
    leftover_text = []
    for uuid, text_info in index.items():
        leftover_text.append(text_info['work_id'])
    return leftover_text


def cross_check_text(pedurma_index, derge_index):
    prev_vol = 0
    count = 0
    for uuid, pedurma_text in pedurma_index.items():
        text_id = pedurma_text['work_id']
        if text_id == 'D1591':
            print('check')
        if text_id:
            if prev_vol != pedurma_text['span'][0]['vol']:
                cur_base_text = Path(f"./P000009.opf/base/v{int(pedurma_text['span'][0]['vol']):03}.txt").read_text(encoding = 'utf-8')
                prev_vol = pedurma_text['span'][0]['vol']
            pedurma_text_sample = get_text_sample(pedurma_text, cur_base_text)
            derge_texts = get_match_text(derge_index, text_id)
            match_text_uuid = match_text(pedurma_text_sample, derge_texts)
            if match_text_uuid:
                count += 1
                print(f"{text_id} match found..")
                del derge_index[match_text_uuid]
            else:
                logging.info(f"{text_id} match not found in derge index")
        else:
            logging.info(f"{uuid} match not found in derge")
    derge_leftover_text = get_leftover_text(derge_index)
    derge_leftover = to_yaml(derge_leftover_text)
    Path('./derge_leftover.yml').write_text(derge_leftover)
    print(f"Number of text match {count}..")

if __name__ == "__main__":
    pedurma_index_file = from_yaml(Path(f"./updated_index.yml"))
    derge_index_file = from_yaml(Path(f"./P000002.opf/index.yml"))
    pedurma_index = pedurma_index_file['annotations']
    derge_index = derge_index_file['annotations']
    cross_check_text(pedurma_index, derge_index)

