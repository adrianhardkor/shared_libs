#!/usr/bin/env python3
import sys,os,json
import wcommon as wc

import concurrent.futures
import logging
import threading
import time

import requests
import concurrent.futures

def get_wiki_page_existence(wiki_page_url, timeout=10):
    response = requests.get(url=wiki_page_url, timeout=timeout)

    page_status = "unknown"
    if response.status_code == 200:
        page_status = "exists"
    elif response.status_code == 404:
        page_status = "does not exist"

    return wiki_page_url + " - " + page_status

wiki_page_urls = [
    "https://en.wikipedia.org/wiki/Ocean",
    "https://en.wikipedia.org/wiki/Island",
    "https://en.wikipedia.org/wiki/this_page_does_not_exist",
    "https://en.wikipedia.org/wiki/Shark",
]


# 'fn': RUNNER, 'attr'=attr



def THREADER(fn, mylist, attr):
    result = {}
    _FN = attr
    _FN['fn'] = fn
#    for l in mylist.keys():
#        _FN[l] = mylist[l]
    with concurrent.futures.ThreadPoolExecutor() as executor:
        futures = []
        for l in mylist:
            _FN[mylist.keys()[0]] = mylist[mylist.keys()[0]]; # for each in mylist, run as arg
            futures.append(executor.submit(_FN))
        for future in concurrent.futures.as_completed(futures):
            print(future.result())
            print(dir(future))

THREADER(get_wiki_page_existence, {'wiki_page_url':wiki_page_urls})
