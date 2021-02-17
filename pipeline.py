import yaml
from pathlib import Path

from outline_reconstruction import get_new_outline
from reconstruct_index import get_new_index
from cross_check import cross_check_text
from filter_derge_leftover import filter_leftover_text
from filter_text_without_work_id import fix_text_without_work_id
from update_outline import get_updated_index

def from_yaml(yml_path):
    return yaml.safe_load(yml_path.read_text(encoding='utf-8'))

def to_yaml(dict_):
    return yaml.safe_dump(dict_, sort_keys = False, allow_unicode=True)

def update_index(new_index):
    derge_index_file = from_yaml(Path(f"./P000002.opf/index.yml"))
    target_index = new_index['annotations']
    derge_index = derge_index_file['annotations']
    cross_check_text(target_index, derge_index)
    text_found_not_match, text_not_in_target = filter_leftover_text(new_index)
    fix_text_without_work_id(new_index, derge_index, text_not_in_target)
    filter_log = Path('./filter.log').read_text()
    updated_index = get_updated_index(new_index, filter_log)
    new_target_index = updated_index['annotations']
    cross_check_text(new_target_index, derge_index)
    text_found_not_match, text_not_in_target = filter_leftover_text(updated_index)
    fix_text_without_work_id(updated_index, derge_index, text_not_in_target)
    filter_log = Path('./filter.log').read_text()
    updated_index = get_updated_index(updated_index, filter_log)
    text_found_not_match = "\n".join(text_found_not_match)
    text_not_in_target = "\n".join(text_not_in_target)
    Path('./text_found_not_match.txt').write_text(text_found_not_match)
    Path('./text_not_in_target.txt').write_text(text_not_in_target)
    return updated_index

if __name__ == "__main__":
    parma = "pedurma"
    old_outline = from_yaml(Path(f'./old_outline/{parma}_text.yml'))
    text_titles = from_yaml(Path(f'./rkts/{parma}_text_titles.yml'))
    new_outline = from_yaml(Path(f'./new_outline/{parma}_outline.yml'))
    if not new_outline:
        new_outline = get_new_outline(old_outline, text_titles)
        Path(f'./new_outline/{parma}_outline.yml').write_text(to_yaml(new_outline), encoding='utf-8')
    new_index = from_yaml(Path(f'./new_index/{parma}_index.yml'))
    if not new_index:
        new_index = get_new_index(new_outline, text_titles)
        Path(f'./new_index/{parma}_index.yml').write_text(to_yaml(new_index), encoding='utf-8')
    new_index = update_index(new_index)
    Path(f"./new_index/{parma}_index.yml").write_text(to_yaml(new_index), encoding='utf-8')


