#!/usr/bin/env python
import os
import fileinput
from string import maketrans

CEDILLATRANS = maketrans(u'\u015f\u0163\u015e\u0162'.encode('utf8'), u'\u0219\u021b\u0218\u021a'.encode('utf8'))

for root, dirs, files in os.walk("."):
    for file in files:
        if root.endswith("data") and (file.endswith(".csv") or file.endswith(".xml")):
            #print root, file
            for line in fileinput.input(os.path.join(root, file), inplace = 1, backup = '.bak'):
                print line.translate(CEDILLATRANS).rstrip()
