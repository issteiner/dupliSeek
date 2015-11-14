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
filesize_store = {}
filehash_store = {}
filestore4sort = []

refdirfind_is_over = False
suppress_msgs_n_reffiles = False

def print_if_allowed(text):
    if not suppress_msgs_n_reffiles:
        print(text, end="", flush=True)


def printlf_if_allowed(text):
    if not suppress_msgs_n_reffiles:
        print(text)


def find_samesize_in_folders(folders):
    for actual_folder in folders:
        find_samesize_in_a_folder(actual_folder)


def find_samesize_in_a_folder(folder):

    global filesize_store

    print_if_allowed('Gathering files with same size in folder \'{}\'... '.format(folder))

    for dirname, subdirs, filelist in os.walk(folder):
        for filename in filelist:
            fullpath_filename = os.path.join(dirname, filename)
            absolutepath_filename = os.path.abspath(fullpath_filename)
            file_size = os.path.getsize(absolutepath_filename)
            if file_size in filesize_store:
                if absolutepath_filename not in filesize_store[file_size]:  # Avoid false file duplication display in case of very same files (ie. when reference dir is part of dirs)
                     filesize_store[file_size].append(absolutepath_filename)
            else:
                if not refdirfind_is_over:
                    filesize_store[file_size] = [absolutepath_filename]
    
    if 0 in filesize_store.keys():
         del (filesize_store[0])
    printlf_if_allowed('Done.')


def put_reffile_end_marker(store):
    for filelist in store.values():
        filelist.append(REFFILE_END_MARKER)


def find_samehash():
    global filehash_store
    print_if_allowed('Comparing same size files with md5... ')
    for samesize_file_list in filesize_store.values():
        if len(samesize_file_list) > 2 or len(samesize_file_list) > 1 and not refdirfind_is_over:
            filehash_temp_store = {}
            reffiles = True
            for filename in samesize_file_list:
                if filename != REFFILE_END_MARKER:
                    file_hash = calculate_hash(filename)
                    if file_hash in filehash_temp_store:
                        filehash_temp_store[file_hash].append(filename)
                    else:
                        if reffiles:
                            filehash_temp_store[file_hash] = [filename]
                else:
                    reffiles = False
                    put_reffile_end_marker(filehash_temp_store)
                    
            for actual_hash in filehash_temp_store.keys():
                if len(filehash_temp_store[actual_hash]) > 2 or len(filehash_temp_store[actual_hash]) > 1 and not refdirfind_is_over:
                    filehash_store[actual_hash] = filehash_temp_store[actual_hash]
    printlf_if_allowed('Done.')


def calculate_hash(file, blocksize=65536):
    if os.path.isfile(file):
        with open(file, 'rb') as actual_file:
            hasher = hashlib.md5()
            buf = actual_file.read(blocksize)
            while len(buf) > 0:
                hasher.update(buf)
                buf = actual_file.read(blocksize)
            return hasher.hexdigest()

   
def find_duplicated_directories(dir):
    print('Not implemented yet.')


def sort_duplicates():
    global filestore4sort
    if filehash_store != {}:
        for files in filehash_store.values():
            filestore4sort.append(files)
        filestore4sort.sort()


def print_duplicates():
    skip_reffile_print = False
    if filestore4sort != []:
        printlf_if_allowed('The following duplicate files were found')

        for samehash_file_list in filestore4sort:
            if REFFILE_END_MARKER in samehash_file_list and suppress_msgs_n_reffiles:
                skip_reffile_print = True

            print('-' * 40)
            for filename in samehash_file_list:
                if filename != REFFILE_END_MARKER:
                    if not skip_reffile_print:
                        try:
                            print(filename)
                        except UnicodeEncodeError:
                            print('There is a problem with filename(s) in folder \'{}\'. Please check and fix.'.format(
                                os.path.dirname(filename)))
                else:
                    printlf_if_allowed(filename)
                    skip_reffile_print = False
    else:
        print('No duplicate files found.')


def check_if_dirs_exist(dirlist):
    for actdir in dirlist:
        if not os.path.exists(actdir):
            print('\'{}\' is not a valid path. Please verify!'.format(actdir))
            sys.exit(1)


def main():

    global suppress_msgs_n_reffiles
    global refdirfind_is_over
    refdirfind_is_over = False

    parser = argparse.ArgumentParser(description='Find duplicate files or duplicate directories')

    parser.add_argument('-r', '--refdir', metavar='rdir', type=str, nargs=1, required=False,
                        help='Reference directory')
    parser.add_argument('-d', '--dirseek', action='store_true', help='Find duplicate directories')
    parser.add_argument('-q', '--quiet' , action='store_true', help='Suppress status messages and file reference printout')
    parser.add_argument('dir', type=str, nargs='+', help='A directory to find for duplicates in')

    try:
        args = parser.parse_args()
    except Exception as e:
        print(e)
        parser.print_help()

    check_if_dirs_exist(args.dir)

    if args.quiet:
        suppress_msgs_n_reffiles = True

    if args.refdir:
        printlf_if_allowed('Starting reference directory based duplicate find...')
        check_if_dirs_exist(args.refdir)
        find_samesize_in_a_folder(args.refdir[0])
        put_reffile_end_marker(filesize_store)
        refdirfind_is_over = True
        find_samesize_in_folders(args.dir)
    elif args.dirseek:
        printlf_if_allowed('Starting duplicate directory find...')
        find_duplicated_directories(args.dir)
    else:
        printlf_if_allowed('Starting normal directory based duplicate find...')
        find_samesize_in_folders(args.dir)

    find_samehash()
    sort_duplicates()
    print_duplicates()


if __name__ == '__main__':
    main()
