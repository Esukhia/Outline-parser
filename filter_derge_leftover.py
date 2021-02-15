import yaml
from pathlib import Path

def to_yaml(dict_):
    return yaml.safe_dump(dict_, sort_keys = False, allow_unicode=True)

def from_yaml(yml_path):
    return yaml.safe_load(yml_path.read_text(encoding='utf-8'))

def get_text(index):
    leftover_text = []
    for uuid, text_info in index.items():
        leftover_text.append(text_info['work_id'])
    return leftover_text

def filter_leftover_text(new_index):
    text_found_not_match = []
    text_not_in_target = []
    derge_index_file = from_yaml(Path(f"./P000002.opf/index.yml"))
    target_index = new_index['annotations']
    target_texts = get_text(target_index)
    derge_left_over = from_yaml(Path("./derge_leftover.yml"))
    for derge_text in derge_left_over:
        if derge_text in target_texts:
            text_found_not_match.append(derge_text)
        else:
            text_not_in_target.append(derge_text)
    print(len(text_found_not_match), len(text_not_in_target))
    return text_found_not_match, text_not_in_target
    

    
    
