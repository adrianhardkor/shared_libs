#!/usr/bin/env python3
import os
import sys
import wcommon as wc
import json
import re
import soap
import deepdiff

import base64
encoded = base64.b64encode(b'data to be encoded')
print(encoded)
data = base64.b64decode(encoded)
print(data)

