import json
import random

files = ['data/manual_big_dset3.json', 'data/ode_dataset.json']
merged_list = []

for file in files:
    with open(file, 'r') as f:
        data = json.load(f)
        if isinstance(data, list):
            merged_list.extend(data)
        else:
            merged_list.append(data)

with open('data/merged_data.json', 'w') as f:
    json.dump(merged_list, f, indent=4)


def shuffle_dataset(filepath: str):
    with open(filepath, 'r') as f:
        data = json.load(f)
    random.shuffle(data)
    with open(filepath, 'w') as f:
        json.dump(data, f, indent=4)


shuffle_dataset('data/merged_data.json')
