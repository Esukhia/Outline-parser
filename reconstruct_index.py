import yaml
from pathlib import Path
from fuzzy_match import algorithims
from uuid import uuid4


def parse_pg_info(pg_info, type_):
    try:
        return pg_info["span"][type_]
    except:
        return ""


def from_yaml(yml_path):
    return yaml.safe_load(yml_path.read_text())

def to_yaml(dict_):
    return yaml.safe_dump(dict_, sort_keys = False, allow_unicode=True)

def get_char_index(pg_start, pg_end, vol_num):
    pg_start = int(pg_start)
    pg_end = int(pg_end)
    pagination_layer = Path(f"./P000009.opf/layers/v{vol_num:03}/Pagination.yml").read_text()
    pagination_yml = yaml.safe_load(pagination_layer)
    pagination = list(pagination_yml["annotations"].values())
    try:
        start_pg_info = pagination[pg_start - 1]
        end_pg_info = pagination[pg_end - 1]
    except:
        start_pg_info = {}
        end_pg_info = {}
    pg_start = parse_pg_info(start_pg_info, "start")
    pg_end = parse_pg_info(end_pg_info, "end")
    return pg_start, pg_end


def parse_outline_text(texts):
    span = []
    for text_id, text in texts:
        cur_text = {}
        start, end = get_char_index(text["img_loc_start"], text["img_loc_end"], int(text["vol"]))
        cur_text = {"vol": int(text["vol"]), "start": start, "end": end}
        span.append(cur_text)
    return span


def get_similarity(text1, text2):
    similarity = algorithims.cosine(text1,text2)
    return similarity


def restructure_outline(text_durchen, ab_titles):
    texts = []
    prev_title = "ཁྱད་པར་དུ་འཕགས་པའི་བསྟོད་པ།" # tengyur pedurma
    prev_vol = "0"
    cur_text = []
    for text_id, text in text_durchen.items():
        if text['pedurma_title'] == prev_title:
            if text['pedurma_title'] not in ab_titles:
                cur_text.append((text_id, text))
            else:
                texts.append(cur_text)
                cur_text = []
                cur_text.append((text_id,text)) 
        else:
            texts.append(cur_text)
            cur_text = []
            cur_text.append((text_id, text))
        prev_title = text["pedurma_title"]
        prev_vol = text["vol"]
    if cur_text:
        texts.append(cur_text)
    return texts


def get_unique_id():
    return uuid4().hex


def reconstruct_index(outline_texts):
    text_annotations = {}
    uuid_mapping = {}
    cur_text = {}
    for text_num, cur_outline_text in enumerate(outline_texts):
        print(f"{cur_outline_text[0][1]['pedurma_title']} processing..")
        span = parse_outline_text(cur_outline_text)
        uuid = get_unique_id()
        cur_text[uuid] = {
            "parts": {},
            "work_id": cur_outline_text[0][1]['rkts_id'],
            "span": span,
        }
        text_annotations.update(cur_text)
        cur_text = {}
        uuid_mapping[uuid] = cur_outline_text[0][0]
    new_index = {
        "id": get_unique_id(),
        "annotation_type": "index",
        "revision": "00001",
        "annotations": text_annotations,
    }
    print(f"Total {len(text_annotations)} text were found..")
    uuid_map_yml = to_yaml(uuid_mapping)
    Path('./uuid_mapping.yml').write_text(uuid_map_yml)
    return new_index

def get_abnormal_titles(tegyur_pedurma_text_title):
    i = 1
    ab_title = []
    for (r_id, t_id, title) in tegyur_pedurma_text_title[1:]:
        prev_title = tegyur_pedurma_text_title[i-1][2]
        if title == prev_title and i != 1:
            ab_title.append(title)
        i+=1
    return set(ab_title)

def get_new_index(new_outline, text_titles):
    ab_titles = get_abnormal_titles(text_titles)
    outline_texts = restructure_outline(new_outline, ab_titles)
    new_index = reconstruct_index(outline_texts)
    return new_index

if __name__ == "__main__":
    new_index = get_new_index()
    Path("./new_index.yml").write_text(new_index)

