import re
import yaml
from bs4 import BeautifulSoup
from collections import defaultdict
from pathlib import Path
from pyewts import pyewts

converter = pyewts()

def to_yaml(dict_):
    return yaml.safe_dump(dict_, sort_keys = False, allow_unicode=True)

def parse_span(span_poti):
    span = []
    potis = re.split('\+\s', span_poti)
    for poti in potis:
        poti_title = converter.toUnicode(poti)
        print(poti_title)
        span.append(poti_title)
    return span

def parse_item(item):
    cur_text = []
    rkts_id = item.find('rktst').text
    try:
        text_title = converter.toUnicode(item.find('tib').text)
    except:
        text_title = ""
    text_id = item.find('ref').text
    if text_title == '':
        text_title = converter.toUnicode(item.find('coloph').text)
        text_title = text_title.replace('རྫོགས་སོ', '')
        print(text_id)
    cur_text.append((rkts_id, text_id, text_title))
    return cur_text

def parse_rkts(rkts_content):
    rkts_soup = BeautifulSoup(rkts_content, 'xml')
    items = rkts_soup.find_all('item')
    texts = []
    count = 1
    for item in items:
        rkts_id = item.find('rktst').text
        if re.search('\d+', rkts_id):
            count += 1
            cur_text = parse_item(item)
            if cur_text:
                for text in cur_text:
                    texts.append(text)
            else:
                print('rkts')
    return texts

if __name__ == "__main__":
    parma = "peking"
    rkts_content = Path(f'./rkts/{parma}.xml').read_text()
    texts = parse_rkts(rkts_content)
    Path(f'./rkts/{parma}_text_titles.yml').write_text(to_yaml(texts), encoding='utf-8')

