#coding:utf8
'''
Created on Mar 16, 2016

@author: Administrator
'''
# coding=gb18030

import re
import sys
import networkx as nx
import matplotlib.pyplot as plt
from pymongo import MongoClient

reload(sys)
sys.setdefaultencoding('gb18030')

def construct():
    print 'construct department network'
    client = MongoClient('localhost', 27017)
    out = open('f:\\data\\edges_1.txt', 'w')

    path_dict = dict() # 保存边信息:字典嵌套字典
    depart_path_dict = dict()  # 保存部门Path和名称之间的对应关系
    depart_id_dict = dict()  # 保存部门ID和path之间的对应关系，从任务表到部门之间的对应关系：task_owner->department_id->department_path
    employ_id_dict = dict()  # 保存员工工号和部门Id之间的对应关系

    # 获取部门path->名称对应关系：level参数指定获取的几级子部门
    level = 4
    get_department_path(client, level, depart_path_dict)

    # 获取部门id->path对应关系
    get_department_id(client, depart_id_dict)

    # 获取员工工号和部门Id之间的对应关系
    get_employ_id(client, employ_id_dict)

    # 查询任务表，构造边及权重信息
    # 只有同一个Project中的task，才构成不同部门之间的边及权重【权重暂时按人天计算】
    db = client['M1OA_DB']
    task = db.M1OA_taskConn
    pattern = re.compile('([0-9]{2}).+[-]([0-9]+).+[-]([0-9]+)')

    last_p_id = ''
    depart_cnt = dict()
    for doc in task.find().sort('project_oid', 1):
        if last_p_id != doc['project_oid']:
            print 'new project:', doc['project_oid']
            last_p_id = doc['project_oid']
            print depart_cnt
            add_to_path(depart_cnt, path_dict)
            # 初始化部门计数器
            depart_cnt.clear()
        //print '\t', convert_id_to_path(doc['task_owner'], employ_id_dict, depart_id_dict, level)
        path = convert_id_to_path(doc['task_owner'], employ_id_dict, depart_id_dict, level)
        if path not in depart_cnt:
            depart_cnt[path] = 1
        else:
            depart_cnt[path] += 1
    print "====================================="
    exit()
    # print path_dict
    G = nx.Graph()
    for p in path_dict:
        couple = p.split('_')
        if len(couple) == 2 and couple[0] != '' and couple[1] != '':
            print 'add ', couple[0], '===', couple[1], ' to edge'
            G.add_edge(depart_path_dict[couple[0]].decode('gb18030'), depart_path_dict[couple[1]].decode('gb18030'), weight=path_dict[p])
    elarge=[(u,v) for (u,v,d) in G.edges(data=True) if d['weight'] > 10]
    esmall=[(u,v) for (u,v,d) in G.edges(data=True) if d['weight'] <= 10]
    print "=====================================111111111111111111"
    print len(path_dict)
    # print >> out, G.edges()
    for edge in G.edges():
        print >> out, edge[0].decode('gb18030'), ',', edge[1].decode('gb18030'), 
    pos=nx.spring_layout(G,scale=100.0) # positions for all nodes
    nx.draw_networkx_nodes(G,pos,node_size=800)
    # edges
    nx.draw_networkx_edges(G,pos,edgelist=elarge,width=3)
    nx.draw_networkx_edges(G,pos,edgelist=esmall,
                    width=6,alpha=0.5,edge_color='b',style='dashed')
    nx.draw_networkx_labels(G,pos,font_size=20,font_family='sans-serif')
    # plt.axis('off')
    plt.savefig("weighted_graph.png") # save as png
    plt.show() # display

    deg = nx.degree(G)
    sorted_deg = sorted(deg.items(), key=lambda deg:deg[1], reverse=True)
    for d in sorted_deg:
        print d[0], ' degree: ', d[1]

    bet = nx.betweenness_centrality(G)
    best = sorted(bet.items(), key=lambda bet:bet[1], reverse=True)
    for b in best:
        print b[0], '==>', b[1]


def get_department_path(client, level, depart_path_dict):
    db = client['empOrgDb']
    department = db.org_unitConn

    for d in department.find({"is_deleted":"0"}).sort('path', 1):
        # print d['orgUnitID'], d['path'], d['name']
        # if len(d['path']) == level*4:
        print d['orgUnitID'], d['name']
        depart_path_dict[d['path']] = d['name']


def get_department_id(client, depart_id_dict):
    print ''
    db = client['empOrgDb']
    department = db.org_unitConn

    for d in department.find({"is_deleted":"0"}):
        # print d['orgUnitID'], d['path'], d['name']
        print d['path'], d['name']
        depart_id_dict[d['orgUnitID']] = d['path']


def get_employ_id(client, employ_id_dict):
    file_iter = open('F:\\data\\org_member.txt', 'rU')
    for line in file_iter:
        line = line.strip().rstrip('|')                         # Remove trailing comma
        record = line.split('|')
        employ_id_dict[record[2]] = record[3]


def convert_id_to_path(employ_id, employ_id_dict, depart_id_dict, level):
    if employ_id in employ_id_dict:
        department_id = employ_id_dict[employ_id]
        if department_id in depart_id_dict:
            path = depart_id_dict[department_id]
            return path[0:4*level]
        else:
            return ''
    else:
        return ''


def add_to_path(depart_cnt, path_dict):
    l = []
    for key in depart_cnt.keys():
        print key
        l.append(key)
    for i in range(0, len(l)-1):
        for j in range(i+1, len(l)):
            target = '%s_%s' % (l[i], l[j])
            if target in path_dict:
                path_dict[target] += 1
            else:
                target_r = '%s_%s' % (l[j], l[i])
                print target_r
                if target_r in path_dict:
                    path_dict[target_r] += 1
                else:
                    path_dict[target] = 1

if __name__ == "__main__":
    construct()


