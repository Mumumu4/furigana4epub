#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import concurrent.futures
import os
import tempfile
import zipfile

from bs4 import BeautifulSoup

from furigana4epub import yomituki


def unzippen(filename, dst_path):
    input_file = zipfile.ZipFile(filename, 'r')
    input_file.extractall(dst_path)


def zippen(filename, dst_path):
    with zipfile.ZipFile(filename, 'w', compression=zipfile.ZIP_DEFLATED, compresslevel=9) as myzip:
        for root, subfolders, files in os.walk(dst_path):
            for file in files:
                fullpath = os.path.join(root, file)
                myzip.write(fullpath, arcname=os.path.relpath(
                    fullpath, start=dst_path))


def get_file(dir, exts=None, recursive=True):
    file_list = []
    for root, subfolders, files in os.walk(dir):
        for file in files:
            ext = f'.{file.split(".")[-1]}'
            if exts is None or ext in exts:
                file_list.append(os.path.abspath(os.path.join(root, file)))
        if not recursive:
            break
    return file_list


def open_file(file_name):
    with open(file_name, encoding="utf-8") as r:
        source = r.read()
    return source


def write_file(file_name, content):
    with open(file_name, "w", encoding="utf-8", newline='\n') as f:
        f.write(content)


class EpubConvert:
    def __init__(self, filename, blod=False, rp=True,un_ruby=False) -> None:
        self.blod = blod
        self.rp = rp
        self.un_ruby = un_ruby
        self.convert_epub(filename)

    def ruby_html_file(self, file):
        soup = BeautifulSoup(open_file(file), 'lxml',
                             string_containers=yomituki.string_containers)
        if self.blod:
            yomituki.point_ruby_to_blod(soup.body)
        yomituki.ruby_soup(soup.body, self.rp)
        write_file(file, str(soup))
        return float(os.path.getsize(file))/1024
        
    def un_ruby_html_file(self, file):
        soup = BeautifulSoup(open_file(file), 'lxml',
                             string_containers=yomituki.string_containers)
        for ruby in soup.body('ruby'):
            ruby.replace_with(ruby.text)
        write_file(file, str(soup))
        return float(os.path.getsize(file))/1024

    def convert_epub(self, filename):
        name, ext = os.path.splitext(filename)
        print(name, filename)
        with tempfile.TemporaryDirectory(prefix='furigana4epub') as tmp_dir:
            unzippen(filename, tmp_dir)
            file_list = get_file(tmp_dir, {'.html', '.xhtml', })

            with concurrent.futures.ProcessPoolExecutor() as executor:
                fsum = len(file_list)
                fsumlen = len(str(fsum))
                for i, (li, file_size) in enumerate(zip(file_list,
                    executor.map(self.un_ruby_html_file if self.un_ruby else self.ruby_html_file, file_list))):
                    print(f"{str(i+1).zfill(fsumlen)} of {fsum} written: {li} {file_size:.1f}KB")
            print(f'zipping epub file in {tmp_dir}')
            zippen(f'{name}_no_furigana.epub' if self.un_ruby else f'{name}_furigana.epub', tmp_dir)

def main():
    import argparse
    parser = argparse.ArgumentParser(
        description='A Python script to add/remove furigana for Japanese epub books. Using Mecab and Unidic.')
    parser.add_argument(
        'paths', type=str, nargs='+',
        help='Paths of Japanese epub books')
    parser.add_argument(
        '-e', '--extension', default='.epub',
        help='File extension to filter by(default:.epub)')
    parser.add_argument(
        '-r', '--recursive', action='store_true', default=False,
        help='Search through subfolders')
    parser.add_argument(
        '-d', '--remove', action='store_true', default=False,
        help='remove furigana from epub file')
    parser.add_argument(
        '-b', '--blod', action='store_true', default=False,
        help='Covert <ruby> dot to html <b> tag before adding furigana')
    parser.add_argument(
        '-p', '--rp', action='store_false', default=True,
        help='Do not add ruby <rp> tag to provide fall-back parentheses for browsers that do not support display of ruby annotations')
    args = parser.parse_args()

    paths = args.paths
    files = set()
    for path in paths:
        if os.path.isfile(path):
            filename, ext = os.path.splitext(path)
            if args.extension == '' or args.extension == ext:
                files.add(path)
        elif args.recursive:
            files = files.union(get_file(path, {args.extension, }))
        else:
            files = files.union(get_file(path, {args.extension, }, False))

    for filename in files:
        print("prosessing started")
        EpubConvert(filename, args.blod, args.rp,args.remove)
        print("prosessing completed")
        
if __name__ == '__main__':
    main()

