# -*- coding: utf-8 -*-

import sys, os
import re
from asyncore import write


if len(sys.argv) < 2:
    print("Invalid arguments!\nUsaeg: {0} <input>".format(os.path.basename(sys.argv[0])))
    exit()


(_, _, filenames) = os.walk(sys.argv[1]).next()
parsejson = {}
for input_file in filenames:
    print("Proccesing " + input_file)
    file_text = open(os.path.join(sys.argv[1], input_file)).read()
    file_text = file_text.replace("’", "'").replace("“", "\"").replace("”","\"").replace("…", "...").replace("‘", "\"").replace("—","-")
    
    
    with open(os.path.join(sys.argv[1], input_file), 'w+') as f:
        f.write(file_text)
    
