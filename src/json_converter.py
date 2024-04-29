import argparse

def convert_json_to_jsonl(input_file, output_file):
    import orjson
    from tqdm import tqdm
    import colorama
    print(f'{colorama.Fore.GREEN}Converting {input_file} to {output_file}{colorama.Style.RESET_ALL}')
    print_sample = True
    with open(input_file, 'r') as f:
        data = orjson.loads(f.read())
        progress_bar = tqdm(data, desc=f'Converting {input_file} to {output_file}', unit='record')
        with open(output_file, 'w') as f:
            for record in progress_bar:
                text = ''
                if 'content' in record:
                    content = record['content']
                if 'title' in record:
                    title = record['title']
                if isinstance(content, str):
                    f.write(orjson.dumps({'text':title+'\n'+content}).decode('utf-8') + '\n')
                elif isinstance(content, list):
                    if print_sample:
                        print_sample = False
                        print(record)
                    for text in content:
                        f.write(orjson.dumps({'text':title+' '+text}).decode('utf-8') + '\n')
    print(f'{colorama.Fore.GREEN}Conversion completed{colorama.Style.RESET_ALL}')

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Convert JSON to JSONL')
    parser.add_argument('--input', type=str, help='Input JSON file or dir')
    parser.add_argument('--output', type=str, help='Output JSONL dir')

    if __name__ == '__main__':
        parser = argparse.ArgumentParser(description='Convert JSON to JSONL')
        parser.add_argument('--input', type=str, help='Input JSON file or dir')
        parser.add_argument('--output', type=str, help='Output JSONL dir')
        parser.add_argument('--num_workers', type=int, default=8, help='Number of workers')
        args = parser.parse_args()

        import os
        os.makedirs(args.output, exist_ok=True)
        is_file = os.path.isfile(args.input)
        if is_file:
            output_file = os.path.join(args.output, os.path.basename(args.input).replace('.json', '.jsonl'))
            convert_json_to_jsonl((args.input, output_file))
        else:
            from multiprocessing import Pool
            with Pool(args.num_workers) as p:
                p.starmap(convert_json_to_jsonl, [(os.path.join(args.input, f), os.path.join(args.output, f.replace('.json', '.jsonl')) ) for f in os.listdir(args.input)])
            print('All done')
