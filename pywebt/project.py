#coding:utf8
'''
Created on Mar 18, 2016

@author: Administrator
'''
import sys
import networkx as nx
from pymongo import MongoClient
import datetime

reload(sys)
sys.setdefaultencoding('gb18030')
client = MongoClient('localhost', 27017)

#该模块需要在空间上优化，及做服务器端缓存

def getSomeData(limit):
    db = client['M1OA_DB']
    conn = db.M1OA_projectConn
    proj = {}   #project information
    timeInfo = {}
    for p in conn.find({'percent_complete': {'$ne': '0%' }}):
        begin = dateF(p['actual_start_date'])
        end =  dateF(p['actual_finish_date'])
        tmp1 = { 'pid': p['projectManage_oid'], 'style': 1 }
        tmp2 = { 'pid': p['projectManage_oid'], 'style': -1 }
        timeInfo[begin] = [tmp1] if begin not in timeInfo else append(timeInfo[begin], tmp1)
        timeInfo[end] = [tmp2] if end == '' or end not in timeInfo else append(timeInfo[end], tmp2)
        proj[p['projectManage_oid']] = { 'id': p['projectManage_oid'], 'begin':begin, 'end':end, 'name':p['projectManage_name'] }
    #get links,    project all information
    P = Path()
    task = db.M1OA_taskConn
    oldPid = ''
    links = {}    # link string    global
    paths = {}    # path list        local
    for doc in task.find().sort('project_oid', 1):
        if oldPid != doc['project_oid']:
            oldPid = doc['project_oid']
            Range(paths, links) 
            if oldPid in proj: proj[oldPid]['unit'] = paths.copy() 
            paths.clear()
        path = P.getPath(doc['task_owner'], 4)
        if path == '': continue
        paths[path] = 1 if path not in paths else paths[path] + 1
    #get time information
    tm = list(timeInfo)
    tm.sort()
    if tm[0] == '':tm.remove('')
    value = [0]
    table = [ (t, plus(value, reduce(lambda a,b : a + len(proj[b['pid']]) * b['style'], timeInfo[t], 0))) for t in tm ]
    return [getG(links, P.Path, limit), table, proj, P.Path]

#获取某时间段网络
def getNetworkPart(t1, t2):
#    t1 = '2007-03-23'
#    t2 = '2008-01-23'
    data = getProjectUnit(None, t1, t2)
    info = data['proj']
    path = data['path']
    links = {}
    for line in info:
        if 'unit' in info[line]:Range(info[line]['unit'], links) 
    return getG(links, path, 0)
    
    
#    ************************************************************
#lines - "xxx_xxx", _path - {path:name}
def getG(lines, _path, limit):
    G = nx.Graph()
    nodes = {}  #索引
    index = 0
    for line in lines:
        sp = line.split("_")
        if len(sp)<2: continue
        n1 = _path[sp[0]]
        n2 = _path[sp[1]]
        if n1 not in nodes:
            nodes[n1] = index
            index += 1
        if n2 not in nodes:
            nodes[n2] = index
            index += 1
        if lines[line] < limit: continue
        G.add_edge(nodes[ n1 ], nodes[ n2 ], wight=int(lines[line]))
    return { 'G': G, 'nodes': nodes}

def getProjectInfo():
    db = client['M1OA_DB']
    proj = db.M1OA_projectConn
    data = {}
    for p in proj.find({'percent_complete': {'$ne': '0%' }}):
        data[p['projectManage_oid']] = { 'id': p['projectManage_oid'], 'begin':dateF(p['actual_start_date']),
                                         'end':dateF(p['actual_finish_date']), 'name':p['projectManage_name'] }
    return data    

#获取工程获取参与部门信息：时间、部门列表,t1,t2 - 起始时间
def getProjectUnit(proj, t1, t2):
    P = Path()
    db = client['M1OA_DB']
    task = db.M1OA_taskConn
    proj = proj if proj != None else getProjectInfo()
    
    _ls = list(proj) if t1 == None else [ x for x in proj if not (dateL(proj[x]['begin'], t2) or dateL(t1, proj[x]['end'])) ]
    oldPid = ''
    paths = {}    # path list        local

    data = {}
    for doc in task.find({ 'project_oid': {"$in": _ls}}).sort('project_oid', 1):
        if oldPid != doc['project_oid']:
            oldPid = doc['project_oid']
            if oldPid not in _ls: 
                paths.clear()
                continue
            data[oldPid] = { 'unit': paths.copy() } 
            paths.clear()
        path = P.getPath(doc['task_owner'], 4)
        if path == '': continue
        paths[path] = 1 if path not in paths else paths[path] + 1
    print len(data)
    return { 'proj':data, 'path':P.Path }

def dateT(_date): return datetime.datetime.strptime(_date, '%Y-%m-%d')
#later time, 1 later than 2
def dateL(_date1, _date2): 
    _date2 = _date2 if _date2 != '' else datetime.datetime.now().strftime('%Y-%m-%d')
    return datetime.datetime.strptime(_date1, '%Y-%m-%d') > datetime.datetime.strptime(_date2, '%Y-%m-%d')

def getTimeValue():
    db = client['M1OA_DB']
    proj = db.M1OA_projectConn
    data = {}
    timeInfo = {}
    for p in proj.find({'percent_complete': {'$ne': '0%' }}):
        begin = dateF(p['actual_start_date'])
        end =  dateF(p['actual_finish_date'])
        data[p['projectManage_oid']] = { 'id': p['projectManage_oid'], 'begin':begin, 'end':end, 'name':p['projectManage_name'] }
        tmp1 = { 'pid': p['projectManage_oid'], 'style': 1 }
        tmp2 = { 'pid': p['projectManage_oid'], 'style': -1 }
        timeInfo[begin] = [tmp1] if begin not in timeInfo else append(timeInfo[begin], tmp1)
        timeInfo[end] = [tmp2] if end == '' or end not in timeInfo else append(timeInfo[end], tmp2)        
    unit = getProjectUnit(data)
    
    tm = list(timeInfo)
    tm.sort()
    if tm[0] == '':tm.remove('')
    value = [0]
    table = [ (t, plus(value, reduce(lambda a,b : a + len(unit[b['pid']]) * b['style'], timeInfo[t], 0))) for t in tm ]
    return [table, data]

def getNetwork():
    P = Path()
    db = client['M1OA_DB']
    task = db.M1OA_taskConn
    
    oldPid = ''
    links = {}    # link string    global
    paths = {}    # path list        local
    for doc in task.find().sort('project_oid', 1):
        if oldPid != doc['project_oid']:
            oldPid = doc['project_oid']
            Range(paths, links) 
            paths.clear()
        path = P.getPath(doc['task_owner'], 4)
        if path == '': continue
        paths[path] = 1 if path not in paths else paths[path] + 1
    return links

def plus(d, i): # like i++,not only return value after plus, but change old value - &
    d[0] += i
    return d[0]

def dateF(_date):
    if _date == '': return ''
    sp = _date.encode('utf8').split('-')
    return '20' + '%02d'% int(sp[0].replace('年', '')) + '-' + '%02d'% int(sp[1].replace('月', '')) + '-' + '%02d'% int(sp[2].replace('日', ''))


def getNetworkG():
    P = Path()
    db = client['M1OA_DB']
    task = db.M1OA_taskConn
    
    oldPid = ''
    links = {}    # link string    global
    paths = {}    # path list        local
    for doc in task.find().sort('project_oid', 1):
        if oldPid != doc['project_oid']:
            oldPid = doc['project_oid']
            Range(paths, links)            
            paths.clear()
        path = P.getPath(doc['task_owner'], 4)
        if path == '': continue
        paths[path] = 1 if path not in paths else paths[path] + 1
        
    G = nx.Graph()
    for line in links:
        couple = line.split('_')
        if len(couple) != 2 or couple[0] == '' or couple[1] == '': continue  
        if couple[0] == '0000000100050002' or couple[1] == '0000000100050002': continue # u'M1测试账号'
        G.add_edge(P.Path[couple[0]].decode('gb18030'), P.Path[couple[1]].decode('gb18030'), weight=links[line])   
#    write_network(G)
    return G

def write_network(G, filename = 'tempNet.edges'):
    fp = open(filename, 'w')
    for ln in G.edges(data = True): fp.write(str(ln[0]) + ',' + str(ln[1]) + ',' + str(ln[2]['weight']) + '\n')
    fp.close()
    
#_paths - list of unit 
def Range(_paths, _links):
    items = [key for key in _paths]
    for i in range(0, len(items) - 1):
        for j in range(i + 1, len(items)):
            link = '%s_%s' % (items[i], items[j])
            linkr = '%s_%s' % (items[j], items[i])
            if link in _links:
                _links[link] += 1
            else:
                if linkr in _links:
                    _links[linkr] += 1
                else:
                    _links[link] = 1


class Path():
    def __init__(self):
        self.Unit = {}        # unitId - path
        self.Path = {}        # path - name
        self.People = {}      # people - unitId
        self.main()
    def main(self):
#        client = MongoClient('localhost', 27017)
        db = client['empOrgDb']
        department = db.org_unitConn
        for d in department.find({"is_deleted":"0"}):
            self.Path[d['path']] = d['name']
            self.Unit[d['orgUnitID']] = d['path']
        file_iter = open('F:\\data\\org_member.txt', 'rU')
        for line in file_iter:
            line = line.strip().rstrip('|')                         # Remove trailing comma
            record = line.split('|')
            self.People[record[2]] = record[3]
        
    def getPath(self, user, level):
        if user not in self.People: return ''
        unit = self.People[user]
        if unit not in self.Unit: return ''
        return self.Unit[unit][0 : 4 * level]
            
    
    pass

def append(ls, value): 
    ls.append(value)
    return ls


#getNetworkPart(None, None)
dt = datetime.datetime.now()
#print [getNetwork(),getTimeValue()]
#print getSomeData()
#getProjectUnit(None)
#getNetworkPart(None, None)

print datetime.datetime.now()-dt
#print getAll()[1]
#getTimeValue()
#getNetwork()
#    print 'End!'
