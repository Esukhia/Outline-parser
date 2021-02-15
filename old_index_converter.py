import yaml
import csv
import re
from github import Github
from pathlib import Path
from collections import defaultdict


def to_yaml(dict_):
    return yaml.safe_dump(dict_, sort_keys = False, allow_unicode=True)

def get_vol(vol):
    return int(re.search('\d+', vol)[0])


def get_span(spans):
    Span = []
    for span in spans:
        cur_vol = {}
        cur_vol['vol'] = get_vol(span['vol'])
        cur_vol['start'] = span['span']['start']
        cur_vol['end'] = span['span']['end']
        Span.append(cur_vol)
    return Span


def get_new_annotation(annotation):
    new_annotation = {}
    uuid = annotation["id"]
    new_annotation[uuid] = {
        'parts': annotation['parts'],
        'work_id': annotation['work'],
        'span': get_span(annotation['span'])
    }
    del annotation["id"]
    return new_annotation


def construct_new_layer(old_layer_content, layer):
    old_layer_yml = yaml.safe_load(old_layer_content)
    annotations = old_layer_yml["annotations"]
    new_annotations = {}
    for annotation in annotations:
        new_annotation = {}
        new_annotation = get_new_annotation(annotation)
        new_annotations.update(new_annotation)
    new_index = {
        "id": old_layer_yml["id"],
        "annotation_type": layer,
        "revision": "00001",
        "annotations": new_annotations,
    }
    return new_index
    
if __name__ == "__main__":
    old_layer_content = Path('./P000002.opf/index.yml').read_text()
    layer = 'index'
    new_index = construct_new_layer(old_layer_content, layer)
    new_index_yml = to_yaml(new_index)
    Path('./derge_index.yml').write_text(new_index_yml)
