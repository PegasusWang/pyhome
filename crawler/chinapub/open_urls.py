#!/usr/bin/env python
# -*- coding:utf-8 -*-

import webbrowser
import sys


def open_urls(filepath):
    with open(filepath, 'r') as f:
        for line in f:
            if line.strip() and 'http' in line:
                raw_input()
                print(line)
                webbrowser.open_new_tab(line.strip())

if __name__ == '__main__':
    try:
        filename = sys.argv[1]
    except IndexError:
        filename = ""
    open_urls(filename)
