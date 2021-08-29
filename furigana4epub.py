#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import argparse
import concurrent.futures
import datetime
import os
import tempfile
import zipfile

from bs4 import BeautifulSoup

import yomituki

parser = argparse.ArgumentParser(
    description='This script is written for adding furigana to Japanese epub books.')
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
    '-d', '--em', action='store_true', default=False,
    help='Covert <ruby> dot to html <em> tag before adding furigana')
parser.add_argument(
    '-p', '--rp', action='store_false', default=True,
    help='Do not add ruby <rp> tag to provide fall-back parentheses for browsers that do not support display of ruby annotations')
parser.add_argument(
    '-q', '--quiet', action='store_true', default=False,
    help='Be quiet')
args = parser.parse_args()


def unzippen(filename, dst_path):

    input_file = zipfile.ZipFile(filename, 'r')
    input_file.extractall(dst_path)


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


def zippen(name, file_path, ext='.zip'):

    with zipfile.ZipFile(name+ext, 'w', compression=zipfile.ZIP_DEFLATED, compresslevel=9) as myzip:
        for root, subfolders, files in os.walk(file_path):
            for file in files:
                fullpath = os.path.join(root, file)
                myzip.write(fullpath, arcname=os.path.relpath(
                    fullpath, start=file_path))


def open_file(file_name):

    with open(file_name, encoding="utf-8") as r:
        source = r.read()
    return source


def converter(file):

    soup = BeautifulSoup(open_file(file), 'lxml',
                         string_containers=yomituki.string_containers)
    if args.em:
        yomituki.point_ruby_to_em(soup.body)
    yomituki.ruby_soup(soup.body, args.rp)
    write_file(file, str(soup))
    return float(os.path.getsize(file))/1024


def write_file(file_name, content):

    with open(file_name, "w", encoding="utf-8", newline='\n') as f:
        f.write(content)


if __name__ == '__main__':

    paths = args.paths
    files = set()
    for path in paths:
        if os.path.isfile(path):
            fileName, fileExt = os.path.splitext(path)
            if args.extension == '' or args.extension == fileExt:
                files.add(path)
        elif args.recursive:
            files = files.union(get_file(path, {args.extension, }))
        else:
            files = files.union(get_file(path, {args.extension, }, False))
    epub_list = sorted(files)

    for filename in epub_list:
        name, ext = os.path.splitext(filename)
        print(name, filename)
        with tempfile.TemporaryDirectory(prefix='furigana4epub') as tmp_dir:
            unzippen(filename, tmp_dir)
            file_list = get_file(tmp_dir, {'.html', '.xhtml', })
            print("prosessing started")

            with concurrent.futures.ProcessPoolExecutor() as executor:
                # tasks = {executor.submit(converter,li) for li in file_list}
                # concurrent.futures.wait(tasks)
                fsum = len(file_list)
                fsumlen = len(str(fsum))

                for i, (li, file_size) in enumerate(zip(file_list, executor.map(converter, file_list))):
                    time = datetime.datetime.today()
                    if not args.quiet:
                        print(
                            f"{str(i+1).zfill(fsumlen)} of {fsum} {time:%H:%M:%S}||written: {li} {file_size:.1f}KB")

            print(f'zipping epub file in {tmp_dir}')
            zippen(name, tmp_dir, '_furigana.epub')
            print("prosessing completed")
