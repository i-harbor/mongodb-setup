#!/usr/bin/Python
# -*- coding: utf-8 -*-

'''
'@file: collection.py
'@author: liyunting
'''

from mongoengine import *

'''
'在db中创建一个collection
'User_bucket : collection名
'并定义collection中每个doc的字段及其类型
'''
class Mybucket(DynamicDocument):
	na = StringField(required = True)                # name, filename or directorypath
	fod = BooleanField(required = True)              # file or directory
	did = ObjectIdField()                            # the objectid of directory where file or directory resides
	si = LongField()                                 # size, the size of file
	ult = DateTimeField()                            # uploadtime, the upload time of file or the create time of directory
	upt = DateTimeField()                            # updatetime, the last update time of the file
	dlc = IntField()                                 # downloadcount, the download times of file
	bac = ListField(StringField())                   # backup list, the backup destinations of file
	arc = ListField(StringField())                   # archive list, the archival destinations of file
	sh = BooleanField()                              # shared, whether the file can be shared
	shp = StringField()                              # share password
	stl = BooleanField()                             # share time limit, whether the file has a limit of shared time
	sst = DateTimeField()                            # share start time
	set = DateTimeField()                            # share end time

