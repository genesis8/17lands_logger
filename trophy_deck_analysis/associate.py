import glob
import pandas

# 保存済みのデッキリストのパスを読み込み
# 今回はKHMのデッキ2281個を使用
path=r"C:\Users\田中太郎\Documents\Mtg\データ\成績優秀デッキ\KHM\deck_txt"
files = glob.glob(path + "/**/*.txt",recursive=True)

# デッキIDと採用カードの縦長データ
deckdata = pandas.DataFrame(columns=["deckid","card","num"])

# ファイルを読み込んでメインデッキをデータフレーム化する関数
def append_deckdata(filename):
    # テンポラリーのデッキデータフレームを作成
    deckdata = pandas.DataFrame(columns=["deckid","card","num"])
    # デッキIDは拡張子ぬきファイル名
    deck_id = filename.split("\\")[-1].split(".")[0]
    f = open(filename)
    line = f.readline()
    while line:
        l = line.strip()
        if (l == ""):
            break
        (num,name) = l.split(" ",1)
        deckdata = deckdata.append({"deckid":deck_id,"card":name,"num":int(num)},ignore_index=True)
        line = f.readline()
    f.close()
    return deckdata

# すべてのデッキを読み込む
i = 1
for line in files:
    print(str(i) + ":" + line)
    tmpdata = append_deckdata(line)
    deckdata = pandas.concat([deckdata,tmpdata])
    i = i + 1

# 学習用に有無のみ分かるデータフレームへ
# deckdata_bool = deckdata.assign(umu=True).drop("num",axis=1)

# 横長データに変換
deckdata_group = deckdata.groupby(['deckid','card'])['num'].sum()
deckdata_h1 = deckdata_group.unstack().reset_index().fillna(0).set_index('deckid')
deckdata_h2 = deckdata_h1.apply(lambda x:x>0)

###### アソシエーション分析（ここ以降は理解してない） #####
from mlxtend.frequent_patterns import apriori
from mlxtend.frequent_patterns import association_rules

# アプリオリによる分析
freq_items1 = apriori(deckdata_h2, min_support = 0.06, use_colnames = True)

# アソシエーションルールの抽出
a_rules1 = association_rules(freq_items1, metric = "lift",min_threshold = 1)

# リフト値でソート
a_rules1 = a_rules1.sort_values('lift',ascending = False).reset_index(drop=True)
