"""
用中華郵政 3+3 轉碼軟體的資料檔重新產生 index.html

用法：
  python tools/build.py <DBF 資料夾路徑>

需要的檔案：rall1.dbf（投遞範圍）、uroad.dbf（路名錯字對照）、Ver.txt（資料版本）
"""
import sys, os, re, json, gzip, base64, collections
sys.path.insert(0, os.path.dirname(__file__))
from dbf import read

CITY_EN = {'臺北市':'Taipei City','基隆市':'Keelung City','新北市':'New Taipei City','連江縣':'Lienchiang County','宜蘭縣':'Yilan County','釣魚臺':'Diaoyutai','新竹市':'Hsinchu City','新竹縣':'Hsinchu County','桃園市':'Taoyuan City','苗栗縣':'Miaoli County','臺中市':'Taichung City','彰化縣':'Changhua County','南投縣':'Nantou County','嘉義市':'Chiayi City','嘉義縣':'Chiayi County','雲林縣':'Yunlin County','臺南市':'Tainan City','高雄市':'Kaohsiung City','南海諸':'South China Sea Islands','澎湖縣':'Penghu County','金門縣':'Kinmen County','屏東縣':'Pingtung County','臺東縣':'Taitung County','花蓮縣':'Hualien County'}

def main(src):
    fl, n, rows = read(os.path.join(src, 'rall1.dbf'))
    I = {f[0]: i for i, f in enumerate(fl)}
    tree = collections.OrderedDict(); en = {}
    for r in rows:
        c, a, rd = r[I['CITY']].strip(), r[I['AREA']].strip(), r[I['ROAD']].strip()
        sc = re.sub(r'[\s　]+', '', r[I['SCOOP']])
        tree.setdefault(c, collections.OrderedDict()).setdefault(a, collections.OrderedDict()).setdefault(rd, []).append([r[I['ZIPCODE']].strip(), sc])
        if r[I['EAREA']].strip(): en.setdefault('a|'+c+a, r[I['EAREA']].strip())
        if r[I['EROAD']].strip(): en.setdefault('r|'+c+a+rd, r[I['EROAD']].strip())
    D = [[c, CITY_EN.get(c, ''), [[a, en.get('a|'+c+a, ''), [[rd, en.get('r|'+c+a+rd, ''), v] for rd, v in A.items()]] for a, A in C.items()]] for c, C in tree.items()]
    fl2, n2, u = read(os.path.join(src, 'uroad.dbf')); J = {f[0]: i for i, f in enumerate(fl2)}
    al = collections.OrderedDict()
    for r in u:
        c, a, w, ok = (r[J[k]].strip() for k in ('CITY', 'AREA', 'ROAD', 'ROAD1'))
        if not w or w == ok or '�' in w or '？' in w: continue
        if c in tree and a in tree[c] and ok in tree[c][a]: al.setdefault(c+'|'+a, {})[w] = ok
    ver = open(os.path.join(src, 'Ver.txt')).read().strip()
    js = json.dumps({'v': ver, 'd': D, 'a': al}, ensure_ascii=False, separators=(',', ':'))
    b64 = base64.b64encode(gzip.compress(js.encode('utf-8'), 9)).decode()
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    tpl = open(os.path.join(root, 'tools', 'template.html'), encoding='utf-8').read()
    open(os.path.join(root, 'index.html'), 'w', encoding='utf-8').write(tpl.replace('__DATA__', b64))
    print(f'完成：資料版本 {ver}，{n} 條投遞範圍 → index.html')

if __name__ == '__main__':
    if len(sys.argv) < 2: sys.exit(__doc__)
    main(sys.argv[1])
