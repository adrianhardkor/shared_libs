#!/usr/bin/env python3
import os
import sys
import wcommon as wc
import json
import re

wc.PARA_CMD_LIST(['show chassis hardware | display json | no-more'], '10.88.245.10', 'juniper_junos', 'ansible', password='An5!bleAXEss', quiet=False,ping=False)

# wc.PARA_CMD_LIST(['show cable modem detail', 'show cable modem noise', 'show cable modem phy'], '10.88.232.16', 'commscope', 'root', password='wowlabs12', quiet=False,ping=False)
