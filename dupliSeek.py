#! /usr/bin/env python3

# Originally taken from:
# http://www.pythoncentral.io/finding-duplicate-files-with-python/
# Original Auther: Andres Torres

# Adapted to only compute the md5sum of files with the same size

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
    # Dups in format {hash:[names]}
    for dirname, subdirs, filelist in os.walk(folder):
#        print('Scanning %s...' % dirname)
        for filename in filelist:
            # Get the fullpath_filename to the file
            fullpath_filename = os.path.join(dirname, filename)
            file_size = os.path.getsize(fullpath_filename)
            # Add or append the file path
            if file_size in samesize_files:
                samesize_files[file_size].append(fullpath_filename)
            else:
                samesize_files[file_size] = [fullpath_filename]

def find_same_hash():
    print('Comparing files with the same size...')
    for samesize_file_list in samesize_files.values():
        if len(samesize_file_list) > 1:
            for filename in samesize_file_list:
#                print('    {}'.format(filename))
                file_hash = calculate_hash(filename)
                if file_hash in samehash_files:
                     samehash_files[file_hash].append(filename)
                else:
                    samehash_files[file_hash] = [filename]

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
    found_duplicate = False
    for samehash_file_list in samehash_files.values():
        if len(samehash_file_list) > 1:
            found_duplicate = True
            print('___________________')
            for filename in samehash_file_list:
                print('\t\t%s' % filename)
            print('___________________')
    
    if not found_duplicate:
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
    sys.exit(main())
