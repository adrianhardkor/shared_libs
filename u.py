#!/usr/bin/env python3
import sys,os,json
import wcommon as wc

tryme = {'commands':['show ver'], 'ip':'10.88.240.32', 'username':'ADMIN','password':'ArcLabAdmin','settings_prompt':"([@]+[a-zA-Z0-9\.\-\_]+[>#%]+[ ])",'buffering':'set cli screen-length 0','ping':False}
tryme['quiet'] = True
tryme['exit'] =  ['request system logout user ADMIN']
tryme['exit'] = ['exit']
for ex in tryme['exit']:
    tryme['commands'].append(ex)

i = 1
while i < 16:
  wc.PARA_CMD_LIST(**tryme)
  i += 1
