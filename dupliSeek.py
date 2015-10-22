#!/usr/bin/env python3

# Originally taken from:

# https://github.com/IanLee1521/utilities/blob/master/utilities/find_duplicates.py
# Original Author: Ian Lee

# Changes are
# - globalized hash directories to avoid directory joining
# - some refactoring, renaming, etc

import argparse
import os
import hashlib
import sys

REFFILE_END_MARKER = '|'
size_file_store = {}
hash_file_store = {}
sorted_file_store = []
refdirfind = False


def find_duplicate_files(folders):
    for actual_folder in folders:
        find_same_size(actual_folder)

    find_same_hash()


def find_same_size(folder):
    global size_file_store

    print('Gathering files with same size in folder \'{}\'... '.format(folder), end="")

    for dirname, subdirs, filelist in os.walk(folder):
        for filename in filelist:
            fullpath_filename = os.path.join(dirname, filename)
            file_size = os.path.getsize(fullpath_filename)
            if file_size in size_file_store:
                if fullpath_filename not in size_file_store[file_size]:  # Avoid file duplication when reference dir is part of dirs
                    if not refdirfind:
                        size_file_store[file_size].append(fullpath_filename)
            else:
                if not refdirfind:
                    size_file_store[file_size] = [fullpath_filename]
    
    if 0 in size_file_store.keys():
         del (size_file_store[0])
    print('Done.')


def put_reffile_end_marker():
    global size_file_store
    for filelist in size_file_store.values():
        filelist.append(REFFILE_END_MARKER)


def find_same_hash():
    global hash_file_store
    print('Comparing same size files with md5... ', end="")
    for samesize_file_list in size_file_store.values():
        if len(samesize_file_list) > 1 and not refdirfind or len(samesize_file_list) > 2 and refdirfind:
            temp_hash_file_store = {}
            for filename in samesize_file_list:
                if filename != REFFILE_END_MARKER:
                    file_hash = calculate_hash(filename)
                    if file_hash in temp_hash_file_store:
                        temp_hash_file_store[file_hash].append(filename)
                    else:
                        temp_hash_file_store[file_hash] = [filename]
            for myhash in temp_hash_file_store.keys():
                if len(temp_hash_file_store[myhash]) > 1:
                    hash_file_store[myhash] = temp_hash_file_store[myhash]
    print('Done.')


def calculate_hash(file, blocksize=65536):
    if os.path.isfile(file):
        with open(file, 'rb') as actual_file:
            hasher = hashlib.md5()
            buf = actual_file.read(blocksize)
            while len(buf) > 0:
                hasher.update(buf)
                buf = actual_file.read(blocksize)
            return hasher.hexdigest()


def find_duplicates_in_refdir(refdir, dir):
    global refdirfind
    find_same_size(refdir)
    put_reffile_end_marker()
#     print(size_file_store)
    find_duplicate_files(dir)
#     for item in size_file_store:
#         print(item, size_file_store[item])
#     sys.exit(0)
    refdirfind = True

def find_duplicated_directories(dir):
    # TODO
    pass


def sort_duplicates():
    global sorted_file_store
    if hash_file_store != {}:
        for files in hash_file_store.values():
            sorted_file_store.append(files)
        sorted_file_store.sort()


def print_duplicates():
    if sorted_file_store != []:
        print('The following duplicate files were found')
        for samehash_file_list in sorted_file_store:
            print('-' * 40)
            for filename in samehash_file_list:
                try:
                    print(filename)
                except UnicodeEncodeError:
                    print('There is a problem with filename(s) in folder \'{}\'. Please check and fix.'.format(
                        os.path.dirname(filename)))
    else:
        print('No duplicate files found.')


def check_if_dirs_exist(dirlist):
    for actdir in dirlist:
        if not os.path.exists(actdir):
            print('\'{}\' is not a valid path. Please verify!'.format(actdir))
            sys.exit(1)


def main():
    global refdirfind
    parser = argparse.ArgumentParser(description='Find duplicate files or duplicate directories')

    parser.add_argument('-r', '--refdir', metavar='rdir', type=str, nargs=1, required=False,
                        help='Reference directory')
    parser.add_argument('-d', '--dirseek', action='store_true', help='Find duplicate directories')
    parser.add_argument('dir', type=str, nargs='+', help='A directory to find for duplicates in')

    try:
        args = parser.parse_args()
    except Exception as e:
        print(e)
        parser.print_help()
#     print(args)

    check_if_dirs_exist(args.dir)

    if args.refdir:
        print('Starting reference directory based duplicate find...')
        check_if_dirs_exist(args.refdir)
        find_duplicates_in_refdir(args.refdir[0], args.dir)
    elif args.dirdups:
        print('Starting duplicate directory find...')
        find_duplicated_directories(args.dir)
    else:
        print('Starting normal directory based duplicate find...')
        find_duplicate_files(args.dir)

    sort_duplicates()
    print_duplicates()


if __name__ == '__main__':
    main()
