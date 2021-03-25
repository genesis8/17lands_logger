import glob
import pandas
import numpy

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


# 英語を日本語に変更
# [注意] この部分はKHM依存で作成
dic_file_name = r"C:\Users\田中太郎\Documents\Mtg\tools\17landsログ取得\17lands_logger\trophy_deck_analysis\khm_dic_eng_jap.txt"
dic_file = open(dic_file_name,encoding="utf-8")
line = dic_file.readline()
from collections import defaultdict
dic = defaultdict(lambda: "error")
while line:
    l = line.strip()
    (japan,eng) = l.split(r"/")
    dic[eng] = japan
    line = dic_file.readline()
dic_file.close()

# データフレームに辞書を与えてrepalaceすると、keyにヒットするものはvalueに変換され、それ以外は変更されない
decklist_jap = deckdata.replace(dic)


# 横長データに変換
deckdata_group = decklist_jap.groupby(['deckid','card'])['num'].sum()
deckdata_h1 = deckdata_group.unstack().reset_index().fillna(0).set_index('deckid')
deckdata_h2 = deckdata_h1.apply(lambda x:x>0)
# 土地とかの情報として意味が薄い要素をドロップ
deckdata_h3 = deckdata_h2.drop([
    "平地","島","沼","山","森",
    "冠雪の平地","冠雪の島","冠雪の沼","冠雪の山","冠雪の森",
    "高山の草地","極北の並木","アクスガルドの武器庫","ブレタガルドの要塞","不詳の安息地",
    "イストフェルの門","氷河の氾濫原","ノットヴォルドの眠り塚","シュタルンハイムの大聖堂","高地の森",
    "氷のトンネル","イマースタームの髑髏塚","リトヤラの鏡湖","カーフェルの港","霧氷林の滝",
    "煌積の谷間","スケムファーの古の間","雪原の陥没孔","硫黄のぬかるみ","セルトランドの凍炎",
    "タイライトの聖域","移り変わるフィヨルド","森林の地割れ","世界樹"
    ],axis=1)


###### アソシエーション分析（ここ以降は理解してない） #####
from mlxtend.frequent_patterns import apriori
from mlxtend.frequent_patterns import association_rules

# アプリオリによる分析
freq_items1 = apriori(deckdata_h3, min_support = 0.02, use_colnames = True,max_len=2)

# アソシエーションルールの抽出
a_rules1 = association_rules(freq_items1, metric = "lift",min_threshold = 2.5)

# リフト値でソート
a_rules1 = a_rules1.sort_values('lift',ascending = False).reset_index(drop=True)


###### Excel貼り付け用のデータ作成 ######

# 冗長な偶数行を飛ばす
a_rules2 = a_rules1[::2]

ant = a_rules2['antecedents'].values
ant = [tuple(x)[0] for x in ant]

con = a_rules2['consequents'].values
con = [tuple(x)[0] for x in con]

lift = a_rules2['lift'].values
lift = [x for x in lift]

# 上をExcelにコピペしてアドインのGIGRAPHで描画するといい感じ

###### vis.js用のデータを作成 ######

linklist = [ant,con,lift]
linklist = list(zip(*linklist))

node_id_dict = defaultdict(lambda: -1)
new_node_id = 1
node_list = []
edge_list = []

for link in linklist:
    (word1,word2,w) = link
    
    if w <= 3.000:
        continue
        
    # ノードが新出だったら新規登録
    w1_node_id = node_id_dict[word1]
    if w1_node_id == -1:
        node_id_dict[word1] = new_node_id
        new_node_id = new_node_id + 1
        w1_node_id = node_id_dict[word1]
    
    w2_node_id = node_id_dict[word2]
    if w2_node_id == -1:
        node_id_dict[word2] = new_node_id
        new_node_id = new_node_id + 1
        w2_node_id = node_id_dict[word2]
    
    # エッジのjson要素をstringで作成
    edge_str = "{ from:" + str(w1_node_id) + ", to: " + str(w2_node_id) + ",value: " + str(w) + " },"
    edge_list.append(edge_str)


node_id_dict_swap = {v:k for k, v in node_id_dict.items()}
for key in node_id_dict_swap.keys():
        node_str = "{ id:" + str(key) + ", value: 5, label : \"" + node_id_dict_swap[key] + "\" },"
        node_list.append(node_str)
#lift = [x*10 for x in lift]

# 上のnode_listとedge_listをvis.jsで使用する

'''
###### グラフ描画(失敗) ######

# 対象とする関係を上位50に限定
a = a_rules1.head(20)

# 親ノードの抽出
ant = a['antecedents'].values
ant = [tuple(x) for x in ant]

# 子ノードの抽出
con = a['consequents'].values
con = [tuple(x) for x in con]

# 全ノードのリストアップ
# both = ant + con <-これだと動かなかったので書き替え
both = [x + y for (x,y) in zip(ant,con)]
both = list(set(both))

# networkx のインポート
import networkx as nx

# 関係グラフの初期化
G = nx.DiGraph()

# ノードの追加
for n in both:
  G.add_node(n)

# エッジの追加
for i in range(len(a)):
    item = a.loc[i]
    ant = tuple(item['antecedents'])
    con = tuple(item['consequents'])
    G.add_edge(ant, con)

# グラフ描画
pos = nx.spring_layout(G, k=0.6)

### これが抜けてるのかな？と思ったけど違うらしい
import matplotlib.pyplot as plt
### 文字化けはコレという記事があったが解消せず
import japanize_matplotlib

plt.rcParams['font.family'] = 'MS Gothic'
plt.figure(figsize=(8, 8))
nx.draw_networkx_nodes(G, pos)
nx.draw_networkx_edges(G, pos)
nx.draw_networkx_labels(G, pos,
    horizontalalignment='left', 
    verticalalignment='center')
plt.axis('off')
plt.tight_layout()
plt.show()
'''