#! /usr/bin/env python3

# Originally taken from:

# https://github.com/IanLee1521/utilities/blob/master/utilities/find_duplicates.py
# Original Auther: Ian Lee

# Changes are
# - globalized hash directories to avoid directory joining
# - some refactoring, renaming, etc

import argparse
import os
import sys
import hashlib

def find_duplicates(folders):
    for actual_folder in folders:
        if os.path.exists(actual_folder):
            # Find the same size files and append them to samesize_files dictionary
            find_same_size(actual_folder)
        else:
            print('%s is not a valid path, please verify' % actual_folder)
    find_same_hash()

def find_same_size(folder):
    print('Gathering files with same size... ', end="")
    for dirname, subdirs, filelist in os.walk(folder):
        for filename in filelist:
            # Get the fullpath_filename to the file
            fullpath_filename = os.path.join(dirname, filename)
            file_size = os.path.getsize(fullpath_filename)
            # Add or append the file path
            if file_size in samesize_files:
                samesize_files[file_size].append(fullpath_filename)
            else:
                samesize_files[file_size] = [fullpath_filename]
    print('Done.')

def find_same_hash():
    print('Comparing same size files with md5... ', end="")
    for samesize_file_list in samesize_files.values():
        if len(samesize_file_list) > 1:
            samesizehash_files = {}
            for filename in samesize_file_list:
                file_hash = calculate_hash(filename)
                if file_hash in samesizehash_files:
                     samesizehash_files[file_hash].append(filename)
                else:
                    samesizehash_files[file_hash] = [filename]
            for hash in samesizehash_files.keys():
                if len(samesizehash_files[hash]) > 1:
                    samehash_files[hash] = samesizehash_files[hash]
    print('Done.')

def calculate_hash(file, blocksize=65536):
    actual_file = open(file, 'rb')
    hasher = hashlib.md5()
    buf = actual_file.read(blocksize)
    while len(buf) > 0:
        hasher.update(buf)
        buf = actual_file.read(blocksize)
    actual_file.close()
    return hasher.hexdigest()


def print_duplicates():
    if samehash_files != {}:
        print('Duplicate files found')
        for samehash_file_list in samehash_files.values():
            print('--------------------------------------------------------------')
            for filename in samehash_file_list:
                print(filename)
    else:
        print('No duplicate files found.')

def main():
    global samesize_files
    global samehash_files
    samesize_files = {}
    samehash_files = {}

    parser = argparse.ArgumentParser(description='Find duplicate files')
    parser.add_argument(
        'folders', metavar='dir', type=str, nargs='+',
        help='A directory to parse for duplicates',
        )
    args = parser.parse_args()
 
    find_duplicates(args.folders)
    print_duplicates()

if __name__ == '__main__':
    main()
