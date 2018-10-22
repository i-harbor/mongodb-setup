#!/usr/bin/Python
# -*- coding: utf-8 -*-

from mongoengine import *
from function import *
import ctypes

def main():
	'''
	'连接到mongodb
	'参数：数据库名，ip，端口
	'''
	connect("test0", host = '10.0.86.201', port=27017)

	#文件名，目录
	filename = 'data.txt'
	filedir = '/root/mycephtest'

	dirId = getDirId(filedir)
	object_name = getObjectId(filename, dirId) 
	size = getFileSize(filename, dirId)
	readFromRados(str(object_name), size)

if __name__ == '__main__':
	main()
