input_file_name = '/home/yueyulin/download_skypile.json'
output_file_name = '/home/yueyulin/download_skypile.txt'
pattern = '2021-43'
import json
with open(input_file_name, 'r') as f:
    data = json.load(f)
    with open(output_file_name, 'w') as f:
        for record in data:
            mediaItem = record['mediaItem']
            url = mediaItem['url']
            filename = mediaItem['filename']
            if filename > pattern:
                f.write(f'https://www.modelscope.cn/api/v1/datasets/modelscope/SkyPile-150B/repo?Revision=master&FilePath=data%2F{filename}\n')