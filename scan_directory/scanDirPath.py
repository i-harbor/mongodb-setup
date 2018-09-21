#!/usr/bin/Python
# -*- coding: utf-8 -*-

'''
'@file: scanDirPath.py
'@author: liyunting
'''

import os
from mongoengine import *
from collection import User_bucket
from function import *

# 递归层级，全局变量，用于标明当前处于递归的第几层
recursive_flag = 0

# 跳过文件列表，在该列表中的文件跳过不做处理
# break_names = ['.trashcan', '$RECYCLE.BIN', 'System Volume Information']
break_names = []


def process_one_path(path, cover_mode, system_mode):
	'''
	'对传入的目录进行处理，将目录及目录下的所有文件和子目录的元数据都加入到db中
	'''
	global recursive_flag
	recursive_flag = recursive_flag + 1  # 递归层级加1

	if recursive_flag == 1:
		if isDirExists(path) == False:  # 若目录在数据库中不存在
			rootpath = User_bucket(na = path, fod = False) # 创建对象
			rootpath.save() # 添加到db

	files = os.listdir(path) # 罗列出目录下所有的子目录和文件

	for file in files:
		if file in break_names: # 若是跳过文件
			continue

		current_path = path + '/' +file
		if isSysOrHide(system_mode, file, current_path): # 若是系统文件或者隐藏文件
			continue

		if os.path.isdir(current_path): # 若是目录
			if not isDirExists(current_path): # 若该目录在db中不存在
				parentId = getDirId(path) # 获取父目录的id
				p = User_bucket(na = current_path, fod = False, did = parentId) # 创建对象
				p.save() # 添加到db
			process_one_path(current_path, cover_mode, system_mode) # 继续递归地处理子目录下的文件与目录

		elif os.path.isfile(current_path): # 若是普通文件
			process_one_file(current_path, path, file, cover_mode) # 对文件进行处理

	recursive_flag = recursive_flag - 1  # 该层递归结束，层级减1


def process_one_file(filepath, dir_path, filename, cover_mode):
	'''
	'对普通文件进行处理
	'若该文件记录已在db中存在，按照cover_mode进行覆盖或跳过操作，若文件在db中不存在，则添加到db中
	'''
	if cover_mode: # 覆盖模式
		dirId = getDirId(dir_path) # 获取文件所在目录的id
		size = os.path.getsize(filepath) # 获取文件大小，单位字节
		if isFileExists(filename, dirId): # 若文件在db已存在
			for u in User_bucket.objects(Q(na = filename) & Q(did = dirId)): # 删除原记录
				u.delete()
		f = User_bucket(na = filename, fod = True, did = dirId, si = size) # 添加新纪录
		f.save()

def main():
	'''
	'连接到mongodb
	'参数：数据库名，ip，端口
	'''
	connect("test19", host = '10.0.86.201', port=27017)

	# 设置待扫描的目录路径
	dir_path = 'c:/holyground'

	# 去掉目录路径后的'/'符号
	dir_path = dir_path.rstrip("/")

	# 设置文件覆盖模式，True代表覆盖，False代表跳过
	cover_mode = True

	# 设置系统模式，1代表windows，2代表linux
	system_mode = 1

	# 对目录进行处理
	process_one_path(dir_path, cover_mode, system_mode)


if __name__ == '__main__':
	main()