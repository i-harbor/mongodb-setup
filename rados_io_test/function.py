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
#from win32file import GetFileAttributesW
#from win32con import FILE_ATTRIBUTE_HIDDEN
#from win32con import FILE_ATTRIBUTE_SYSTEM
import ctypes
from mongoengine.context_managers import switch_collection

collection_name = 'bucket0'


class RetType(ctypes.Structure): #rados读写返回值类型
    _fields_ = [('x', ctypes.c_bool),('y', ctypes.c_char_p)]

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
		if pr.count() > 0 :
			p = pr[0]
			return p.id
		else :
			print ("Error: the path", parent_path, "do not exist")
			sys.exit()


def getFileSize(filename, dirId):
	'''
	'获取文件大小并返回
	'''
	global Mybucket
	with switch_collection(Mybucket, collection_name) as Mybucket:
		file = Mybucket.objects(Q(na = filename) & Q(did = dirId))
		if file.count() > 0 :
			f = file[0]
			return f.si
		else :
			print ("Error: the file", filename, "do not exist")
			sys.exit()



def getObjectId(filename, dirId):
	'''
	'获取文件的id并返回
	'''	
	global Mybucket
	with switch_collection(Mybucket, collection_name) as Mybucket:
		file = Mybucket.objects(Q(na = filename) & Q(did = dirId))
		if file.count() > 0 :
			f = file[0]
			return f.id
		else :
			print ("Error: the file", filename, "do not exist")
			sys.exit()		


def isSysOrHide(system, filename, filepath):
	'''
	'判断当前系统下，文件是否为系统文件或隐藏文件
	'参数：system ：系统代号，1 表示 windows 系统， 2 表示 linux系统
	'      filename：文件名
	'若文件是系统文件或是隐藏文件，则返回True，否则返回False
	'''
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
	'''
	if system == 2 :
		if filename.startswith('.'):
			return True
		else:
			return False



def storeToRados(object_name, f, size):
	'''
	'将文件存储为rados对象
	'''
	rados = ctypes.CDLL('./rados.so')
	ToObj = rados.ToObj # CDLL
	ToObj.restype = RetType # declare the expected type returned

	# parameters
	cluster_name = "ceph".encode('utf-8') 
	user_name    = "client.objstore".encode('utf-8') 
	conf_file    = "/etc/ceph/ceph.conf".encode('utf-8') 
	pool_name    = "objstore".encode('utf-8') 
	oid          = object_name.encode('utf-8') 
	mode         = "w".encode('utf-8') # write mode ['w':write,'wf':write full,'wa':write append]
	
	#write into rados
	chunk_size = 10485760 #10M 块大小
	offset     = 0 #起始偏移量
	
	#分块写入
	while offset < size :
		rest_size = size - offset
		if rest_size < chunk_size : #当剩余文件大小不足块大小，全部写入
			data = f.read(rest_size)
			result = ToObj(cluster_name, user_name, conf_file, pool_name, oid, data, mode, ctypes.c_ulonglong(offset)) # return. Type:RetType
			print(result.y.decode())
			if result.x :
				offset = offset + rest_size
			else:
				sys.exit()
		else : #当剩余文件大小超过块大小，写入块大小
			data = f.read(chunk_size)
			result = ToObj(cluster_name, user_name, conf_file, pool_name, oid, data, mode, ctypes.c_ulonglong(offset)) # return. Type:RetType
			print(result.y.decode())
			if result.x :
				offset = offset + chunk_size
			else:
				sys.exit()



def delete_object(object_name):
	'''
	'从rados中删除一个对象
	'''
	rados = ctypes.CDLL('./rados.so')
	DelObj = rados.DelObj # CDLL
	DelObj.restype = RetType # declare the expected type returned

	# parameters
	cluster_name = "ceph".encode('utf-8') # cluster name. type:bytes
	user_name    = "client.objstore".encode('utf-8') # user name. type:bytes
	conf_file    = "/etc/ceph/ceph.conf".encode('utf-8') # config file path. type:bytes
	pool_name    = "objstore".encode('utf-8') # pool名称. type:bytes
	oid          = object_name.encode('utf-8') # object id. type:bytes

	result = DelObj(cluster_name, user_name, conf_file, pool_name, oid) # return. Type:RetType
	print(result.y.decode())
	if not result.x :
		sys.exit()



def readFromRados(object_name, size):
	'''
	'从rados中读取一个对象
	'''
	rados = ctypes.CDLL('./rados.so')
	FromObj = rados.FromObj # CDLL
	FromObj.restype = RetType # declare the expected type returned

	# parameters
	cluster_name = "ceph".encode('utf-8') # cluster name. type:bytes
	user_name    = "client.objstore".encode('utf-8') # user name. type:bytes
	conf_file    = "/etc/ceph/ceph.conf".encode('utf-8') # config file path. type:bytes
	pool_name    = "objstore".encode('utf-8') # pool名称. type:bytes
	oid          = object_name.encode('utf-8') # object id. type:bytes

	offset = 0
	chunk_size = 10485760 #10M 块大小

	#分块读取
	while offset < size :
		rest_size = size - offset #剩余对象大小	
		if rest_size < chunk_size : #当剩余对象大小小于块大小，读取全部剩余对象
			result = FromObj(cluster_name, user_name, conf_file, pool_name, rest_size, oid, ctypes.c_ulonglong(offset)) # return. Type:RetType
			print(result.y.decode())
			if result.x :
				offset = offset + rest_size
			else :
				sys.exit()
		else : #当剩余对象大小大于块大小，读取块大小
			result = FromObj(cluster_name, user_name, conf_file, pool_name, chunk_size, oid, ctypes.c_ulonglong(offset)) # return. Type:RetType
			print(result.y.decode())
			if result.x :
				offset = offset + chunk_size
			else :
				sys.exit()

