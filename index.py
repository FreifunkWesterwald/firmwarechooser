#!/usr/bin/env python3

import json
import sys
import argparse
import os
import time
from os.path import join, getsize

import settings

current_milli_time = lambda: int(round(time.time() * 1000))

def genrate_list_files(files):
    list_files = []
    for name in files:
        if name.startswith('.'):
            continue
        list_files.append(name)
    return list_files

def genrate_index_subdirs(dirs):
    index_subdirs = {}
    for name in dirs:
        index_subdirs[name] = {}
    return index_subdirs

def genrate_index(rootdir, indexpath, readmename):
    index = {}
    index['timestamp'] = current_milli_time()
    for root, dirs, files in os.walk(rootdir):
        # Remove the 'rootdir' part in root and spit it by '/'
        trimmed_root = root[len(rootdir + '/'):]

        if len(trimmed_root) > 0:
            root_parts = trimmed_root.split('/')
            ptr = index
            for part in root_parts:
                ptr = ptr[part]
            index_subdirs = genrate_index_subdirs(dirs)
            for key in index_subdirs.keys():
                ptr[key] = index_subdirs[key]
            list_files = genrate_list_files(files)
            if len(list_files) > 0:
                ptr['files'] = list_files
            if readmename in files:
                ptr['discription'] = readmename
        # Case rootdir
        else:
            index_subdirs = genrate_index_subdirs(dirs)
            for key in index_subdirs.keys():
                index[key] = index_subdirs[key]
            list_files = genrate_list_files(files)
            if len(list_files) > 0:
                index['files'] = list_files
            if readmename in files:
                index['discription'] = readmename

    with open(indexpath, 'w') as f:
        json.dump(index, f, ensure_ascii=False)

def read_timestamp(indexpath):
    if not os.path.isfile(indexpath):
        return 0
    with open(indexpath, 'r') as f:
        index = json.load(f)
    return int(index['timestamp'])

def parse_cmd_args(argv):
    # Set options to default values
    options = {
        'force': False,
        'indexpath': settings.indexpath,
        'datapath': settings.datapath,
        'delta': settings.delta,
        'readmename': settings.readmename
    }
    for arg in argv:
        argsplit = []
        if '=' in arg:
            argsplit = arg.split('=')
        if arg == '-f':
            options['force'] = True
        elif len(argsplit) > 0:
            if argsplit[0] == '--indexpath':
                options['indexpath'] = argsplit[1]
            elif argsplit[0] == '--datapath':
                options['datapath'] = argsplit[1]
            elif argsplit[0] == '--readmename':
                options['readmename'] = argsplit[1]
            elif argsplit[0] == '--delta':
                options['delta'] = int(argsplit[1])
            #else:
                # Error handling
        #else:
            # Error handling
    return options

def main(argv):
    options = parse_cmd_args(argv)
    timestamp = read_timestamp(options['indexpath'])
    if current_milli_time() - timestamp > (options['delta'] * 60 * 1000) or options['force']:
        genrate_index(options['datapath'], options['indexpath'], options['readmename'])
        print("Generation succesfull")

if __name__ == "__main__":
    main(sys.argv)
