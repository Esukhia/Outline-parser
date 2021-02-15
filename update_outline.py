from pathlib import Path
import re
import yaml

def to_yaml(dict_):
    return yaml.safe_dump(dict_, sort_keys = False, allow_unicode=True)

def from_yaml(yml_path):
    return yaml.safe_load(yml_path.read_text(encoding='utf-8'))


def parse_log(log):
    log_parts = log.split(' ')
    log_info = {
        'uuid': log_parts[0][10:],
        'text_id': log_parts[4],
        'similarity': float(log_parts[-1][:4])
    }
    return log_info

def update_text(log_info, target_index):
    if round(log_info['similarity']) >= 95:
        print(log_info['text_id'])
        target_index[log_info['uuid']]['work_id'] = log_info['text_id']
    return target_index

def get_updated_index(target_index_file, filter_log):
    target_index = target_index_file['annotations']
    logs = filter_log.splitlines()
    for log in logs:
        if '%' in log:
            log_info = parse_log(log)
            target_index = update_text(log_info, target_index)
    target_index_file['annotations'] = target_index
    return target_index_file
    

if __name__ == "__main__":
    filter_log = Path('./filter.log').read_text()
    target_index_file = from_yaml(Path(f"./new_index.yml"))
    updated_index = get_updated_index(target_index_file, filter_log)
    Path('./updated_index.yml').write_text(updated_index)
    
