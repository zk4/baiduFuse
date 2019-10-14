from diskcache import Cache
import copy
c =Cache()
c['a']={'subs':set(['1','2'])}
s=c['a']
s['subs'].add('aac')
print(s)
c['a']=s
print(c['a']['subs'])

