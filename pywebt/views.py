#coding:utf8
'''
Created on Mar 10, 2016

@author: Administrator
'''

from __future__ import unicode_literals

import json
from django.shortcuts import render
from django.http import HttpResponse

import net1
 
def people(request):
    List = ['自强学堂', '渲染Json到模板']
    Dict = {'site': '自强学堂', 'author': '涂伟忠'}
    return render(request, 'people.html', {
            'List': json.dumps(List),
            'Dict': json.dumps(Dict)
        })
    
    
def index(request):
    return HttpResponse('寻英大数据挖掘中……')

def hello(request):
    return HttpResponse('Hello moto')

def data_network(request):
    callback = request.GET['callback']
    
    data = net1.getNetwork()
    return HttpResponse('%s(%s)' % (callback, json.dumps(data)), content_type='application/json') 
    
def data_network_part(request):
    callback = request.GET['callback']
    t1 = request.GET['begin']
    t2 = request.GET['end']
    data = net1.getNetworkByTime(t1, t2)
    return HttpResponse('%s(%s)' % (callback, json.dumps(data)), content_type='application/json') 





#    return HttpResponse(json.dumps(name_dict), content_type='application/json')