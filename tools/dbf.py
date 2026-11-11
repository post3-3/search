import struct,sys
def read(fn,limit=None,enc='cp950'):
    f=open(fn,'rb'); h=f.read(32)
    n,hl,rl=struct.unpack('<IHH',h[4:12])
    fields=[]
    while True:
        d=f.read(32)
        if d[0]==0x0d: break
        name=d[:11].split(b'\0')[0].decode('ascii','replace'); t=chr(d[11]); ln=d[16]
        fields.append((name,t,ln))
    f.seek(hl)
    rows=[]
    for i in range(n if limit is None else min(n,limit)):
        r=f.read(rl)
        if not r: break
        if r[0:1]==b'*': continue
        p=1; row=[]
        for name,t,ln in fields:
            v=r[p:p+ln]; p+=ln
            row.append(v.decode(enc,'replace').rstrip() if t in 'CDNLF' else v.hex())
        rows.append(row)
    return fields,n,rows
if __name__=='__main__':
    for fn in sys.argv[1:]:
        fl,n,rows=read(fn,6)
        print('==',fn,n,'rows',fl)
        for r in rows: print('  ',r)
