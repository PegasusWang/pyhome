#!/usr/bin/env python
# -*- coding:utf-8 -*-

import webbrowser


with open('./url.txt', 'r') as f:
    for line in f:
        if line.strip() and 'http' in line:
            raw_input()
            print(line)
            webbrowser.open_new_tab(line.strip())
