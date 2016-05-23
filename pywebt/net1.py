#coding:utf8
'''
Created on Mar 16, 2016

@author: Administrator
'''
import os
import sys
import json
import random
import datetime
import networkx as nx
import community
import matplotlib.pyplot as plt
import project

reload(sys)
sys.setdefaultencoding('utf8')


#根据网络数据获取网络所有信息
def getInfoByG(G, nodes, filter):
    lsDegree = G.degree()
    netInfo = network_calc(G, lsDegree) #网络各项指标信息统计
    lsBetwns = nx.betweenness_centrality(G)
    
    nodeInfo = node_format(nodes, lsDegree, lsBetwns, uint_info())   #节点各项指标信息统计
    
    if filter: network_filter(G, lsDegree) #为了可视化过滤网络
    
    network = networkx_json(nodes, G)       #网络数据
    
    lsDegree = { x.encode('utf8') : lsDegree[nodes[x]] if nodes[x] in lsDegree else 0 for x in nodes } #name：degree
    for l in lsDegree:
        print l, lsDegree[l]
    print len(lsDegree)
    return {'network': network, 'nodes': nodeInfo, 'netInfo': netInfo, 'degree': lsDegree }
#    return {'network': network, 'nodes': nodeInfo, 'netInfo': netInfo }

def getNetwork():
    limit = 1
    Info = project.getSomeData(limit)
    
    G = Info[0]['G']      #索引
    nodes = Info[0]['nodes']
    data = getInfoByG(G, nodes, False)
    data['timeInfo'] = Info[1]
    data['project'] = Info[2]
    data['path'] = Info[3]
    _temp = { x : Info[3][x] for x in Info[3] if Info[3][x] in nodes }
    lsDegree = { x : data['degree'][_temp[x].encode('utf8')] if _temp[x].encode('utf8') in data['degree'] else 0 for x in _temp } #path：degree
    data['degree'] = lsDegree
#    for n in nodes: print n#, lsDegree[n]
    return json.dumps(data)

def getNetworkByTime(t1, t2):
    Info = project.getNetworkPart(t1, t2)
    G = Info['G']      #索引
    nodes = Info['nodes']
    return json.dumps(getInfoByG(G, nodes, True))
    

#网络过滤
def network_filter(G, lsDegree):
    _lsdg = map(lambda x : (x, lsDegree[x]), lsDegree)
    _lsdg.sort(key=lambda x : x[1], reverse=True)
    lsBig = _lsdg[0:3]   #大节点
    _links = G.edges(data = True)
    _wight = { '%s_%s' % (x[0], x[1]) : x[2]['wight'] for x in _links } #边权重
    def removeEdge(x, y):
        key = '%s_%s' % (x, y)
        if key not in _wight or _wight[key] > 8 or _wight[key] == -1: return
        G.remove_edge(x, y)
        _wight[key] = -1
    for node in lsBig:
        _nerbs = G.neighbors(node[0])
        for b in lsBig: 
            if b in _nerbs: _nerbs.remove(b) 
        ls_rank(_nerbs, removeEdge)

def network_calc(G, lsDegree):
    len_nodes = G.number_of_nodes()
    len_edges = G.size()
    avg_degree = reduce(lambda x, y: x + y, lsDegree, 0) / len_nodes
    avg_path = nx.average_shortest_path_length(G) 
    diameter = nx.diameter(G)
    clustering = nx.average_clustering(G)
    len_components = len(nx.strongly_connected_components(G))
    return {'len_nodes': len_nodes, 'len_edges': len_edges, 'avg_degree': avg_degree, 'avg_path': round(avg_path, 2),
             'diameter': diameter, 'clustering': round(clustering, 2), 'len_components': len_components }
    
def node_format(nodes, lsDegree, lsBetwns, units):
    return map(lambda x : { 'name': x, 'numb': nodes[x], 'degree': lsDegree[nodes[x]] if nodes[x] in lsDegree else 0,
                      'btness': round(lsBetwns[nodes[x]], 3) if nodes[x] in lsBetwns else 0, 'nofit': units[x.encode('utf8')] if x.encode('utf8') in units else 0 }, nodes)
#社团信息
def network_communitie(G):
    part = community.best_partition(G)
    values = [part.get(node) for node in G.nodes()]
    nx.draw_spring(G, cmap = plt.get_cmap('jet'), node_color = values, node_size=30, with_labels=False)
    plt.show()
    
def networkx_json_str(nodes, G = None):
    return json.dumps(networkx_json(nodes, G), ensure_ascii=False, indent=2)

def networkx_json(nodes, G):
    links = G.edges(data = True)
    groups = community.best_partition(G)
    part = reduce(lambda x, y : x if x>groups[y] else groups[y], groups, 0) + 1
    modular = community.modularity(groups,G)
    groups = { nodes[x]: groups[nodes[x]] if nodes[x] in groups else part for x in nodes }
    lsN = map(lambda x : { "id" : nodes[x], "name" : x, "group" : groups[nodes[x]] }, nodes)
    lsL = map(lambda x : { "source" : x[0], "target" : x[1], "value" : x[2]['wight'] }, links)
    return { "nodes" : lsN, "links" : lsL, "modular": round(modular, 2), "community": part + 1 }

def filePath(filename):return  os.path.dirname(os.path.abspath(__file__)) + '/' + filename


#部门不配合度
def uint_info():
    fp = open(filePath("unitinfo.txt"), "r")
    units = {}
    for line in fp.readlines():
        sp = line.split(" ")
        if len(sp)==2: units[sp[0]] = sp[1]
    fp.close()
    return units

def ls_rank(ls, callback):
    for i in range(0, len(ls)):
        for j in range(i + 1, len(ls)):
            callback(ls[i], ls[j])

    
def writeTxt(txt, filename = 'write.txt'):
    fp = open(filename, 'w')
    fp.write(str.encode('utf8'))
    fp.close()

def write_network(G, filename = 'tempNet.edges'):
    fp = open(filename, 'w')
    for ln in G.edges(): fp.write(str(ln[0]) + ',' + str(ln[1]) + '\n')
    fp.close()



#dt = datetime.datetime.now()      
getNetwork()
#print datetime.datetime.now()-dt
#
#G1 = nx.Graph()
#G1.add_edge(1, 2)
#G1.add_edge(2, 3)
#G1.add_edge(1, 4)
#G1.add_edge(4, 5)
#print G1.edges()
#
#ls = [1,2,3]
##ls_rank(ls, G.remove_edge)
#if (1, 2) in G1.edges(): G1.remove_edge(1, 2)
#print G1.edges()


#    for line in lines:
#        sp = line.split(",")
#        if len(sp)<3: continue
#        n1 = sp[0].encode("utf8")
#        n2 = sp[1].encode("utf8")
#        if n1 not in nodes:
#            data.append(n1)
#            nodes[n1] = index
#            index += 1
#        if n2 not in nodes:
#            data.append(n2)
#            nodes[n2] = index
#            index += 1
#        if int(sp[2]) < limit: continue
##        print nodes[sp[0]], nodes[sp[1]]
#        G.add_edge(nodes[sp[0]], nodes[sp[1]], wight=int(sp[2]))
#        links.append((nodes[sp[0]], nodes[sp[1]], int(sp[2])))


