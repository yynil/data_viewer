import argparse
import os
import shutil
import heapq

def distribute_files(source_dir, target_dir, num_dirs,suffix=['.json','.jsonl']):
    # 获取源目录中的所有json和jsonl文件
    suffix = tuple(suffix)
    files = [f for f in os.listdir(source_dir) if f.endswith(suffix)]
    file_sizes = {f: os.path.getsize(os.path.join(source_dir, f)) for f in files}

    # 创建目标目录
    if not os.path.exists(target_dir):
        os.makedirs(target_dir)
    
    sub_dirs = [(0,os.path.join(target_dir, str(i))) for i in range(num_dirs)]
    for _,sub_dir in sub_dirs:
        if not os.path.exists(sub_dir):
            os.makedirs(sub_dir)
    
    from tqdm import tqdm
    progress_bar = tqdm(total=len(files), desc='Distributing files')

    for file,size in sorted(file_sizes.items(), key=lambda x: x[1], reverse=True):
        sub_dir_size,sub_dir = heapq.heappop(sub_dirs)
        shutil.copy(os.path.join(source_dir, file), os.path.join(sub_dir, file))
        heapq.heappush(sub_dirs, (sub_dir_size+size,sub_dir))
        progress_bar.update(1)
    progress_bar.close()

    import colorama
    from colorama import Fore
    colorama.init(autoreset=True)
    print(Fore.GREEN + 'Files distributed successfully!')
    for i,(size,sub_dir) in enumerate(sub_dirs):
        print(Fore.GREEN + f'Target directory {i}: {sub_dir}, size: {size} bytes')


def main():
    # 创建ArgumentParser对象
    parser = argparse.ArgumentParser(description='Distribute files from source directory to multiple target directories.')
    
    # 添加参数
    parser.add_argument('--source_dir', type=str, help='The source directory.')
    parser.add_argument('--target_dir', type=str, help='The target directory.')
    parser.add_argument('--num_dirs', type=int, help='The number of target directories.')
    parser.add_argument('--suffix', type=str,nargs="+", help='The suffix of files to distribute.', default=['.json','.jsonl'])
    
    # 解析命令行参数
    args = parser.parse_args()
    
    # 调用distribute_files函数
    distribute_files(args.source_dir, args.target_dir, args.num_dirs)

if __name__ == '__main__':
    main()