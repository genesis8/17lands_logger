import glob
import os
import re

from collections import defaultdict

counter = defaultdict(int)
files = glob.glob("deck_txt/*/*/*")
for line in files:
    #print(line)
    
    #img_dir = os.path.join("deck_img","/".join(line.split("/")[1:2]))
    rank   = line.split("\\")[1]
    color  = line.split("\\")[2]
    #print(color)
    pure = re.sub(r'[a-z]',"",color)
    #print(pure)
    counter[pure]+=1

print(counter)

for k, vs in counter.items():
    print(str(k) + "," + str(vs))
