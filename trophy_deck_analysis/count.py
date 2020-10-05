from collections import defaultdict
import glob

pick_deck_dict = defaultdict(lambda : defaultdict(int))

def add_pick_deck(file):

    print(file)
    
    f = open(file)
    line = f.readline()
    maindeck = True
    while line:
        l = line.strip()

        if (l == ""):
            line = f.readline()
            maindeck = False
            continue

        (num,name) = l.split(" ",1)
        
        if maindeck:
            pick_deck_dict[name]["deck"] += int(num)
        pick_deck_dict[name]["pick"] += int(num)
        
        line = f.readline()
    f.close()

def add_folder(path):
    files = glob.glob(path + "/**/*.txt",recursive=True)
    for line in files:
        print(line)
        add_pick_deck(line)

def add_folder_color(path,color):
    files = glob.glob(path + "/**/*.txt",recursive=True)
    for line in files:
        elem = line.split('\\')
        if color in elem:
            print(line)
            add_pick_deck(line)

def print_rate(filename):
    namerate = defaultdict(int)
    for name in pick_deck_dict.keys():
        rate = pick_deck_dict[name]["deck"] / pick_deck_dict[name]["pick"]
        rate = round( 100 * rate)
        namerate[name] = rate

    sorteddic = sorted(namerate.items(), key=lambda x:x[1], reverse=True)

    f = open(filename,mode="w")

    for name in sorteddic:
        print(str(name[1]) + " " + name[0])
        f.write(str(name[1]) + " " + name[0] + "\n")
    f.close()
