#!/usr/bin/env python
# -*- coding:utf-8 -*-

import requests
import concurrent.futures

URLS = ['http://localhost:8000/test']  * 10

# Retrieve a single page and report the URL and contents
def load_url(url, timeout):
	return requests.get(url, timeout=timeout).text


# We can use a with statement to ensure threads are cleaned up promptly
with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
    # Start the load operations and mark each future with its URL
    future_to_url = {executor.submit(load_url, url, 3): url for url in URLS}
    for future in concurrent.futures.as_completed(future_to_url):
        url = future_to_url[future]
        try:
            data = future.result()
        except Exception as exc:
            print('||||')
            print('%r generated an exception: %s' % (url, exc))
        else:
            print('%r page is %d bytes' % (url, len(data)))
