#!/usr/bin/Python
# -*- coding: utf-8 -*-

'''
'@file: function.py
'@author: liyunting
'说明：需安装pypiwin32模块
'pip install pypiwin32
'''

from mongoengine import *
from collection import Mybucket
import sys
from win32file import GetFileAttributesW
from win32con import FILE_ATTRIBUTE_HIDDEN
from win32con import FILE_ATTRIBUTE_SYSTEM
from mongoengine.context_managers import switch_collection

collection_name = 'bucket0'

def isDirExists(dir_path):
	'''
	'判断dir_path的元数据是否在数据库中已经存在
	'若存在，则返回True，不存在，则返回False
	'''
	global Mybucket
	with switch_collection(Mybucket, collection_name) as Mybucket:
		if Mybucket.objects(na = dir_path).count() > 0: # 根据目录路径进行查询
			return True
		else :
			return False


def isFileExists(filename, dirId):
	'''
	'判断当前文件的元数据是否在数据库中已经存在
	'若存在，则返回True，不存在，则返回False
	'''
	global Mybucket
	with switch_collection(Mybucket, collection_name) as Mybucket:
		if Mybucket.objects(Q(na = filename) & Q(did = dirId)).count() > 0: # 根据文件名以及文件所在路径进行查询
			return True
		else :
			return False


def getDirId(parent_path):
	'''
	'获取文件所在目录的id或者获取目录的父目录的id
	'返回父目录的id
	'''
	global Mybucket
	with switch_collection(Mybucket, collection_name) as Mybucket:
		pr = Mybucket.objects(na = parent_path)
		if pr.count() > 0:
			p = pr[0]
			return p.id
		else:
			print ("Error: the path", parent_path, "do not exist")
			sys.exit()


def isSysOrHide(system, filename, filepath):
	'''
	'判断当前系统下，文件是否为系统文件或隐藏文件
	'参数：system ：系统代号，1 表示 windows 系统， 2 表示 linux系统
	'      filename：文件名
	'若文件是系统文件或是隐藏文件，则返回True，否则返回False
	'''
	if system == 1:
		file_flag = GetFileAttributesW(filepath)
		is_hidden = file_flag & FILE_ATTRIBUTE_HIDDEN
		is_system = file_flag & FILE_ATTRIBUTE_SYSTEM
		if is_hidden == 2 or is_system == 4:
			return True
		else:
			return False
	elif system == 2:
		if filename.startswith('.'):
			return True
		else:
			return False
