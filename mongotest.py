#-*-coding:utf-8-*-

'''
'@file mongotest.py
'@author liyunting
'@version 0.1
'
'This file is to use python3 to connect to mongodb.
'''

import pymongo, sys
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure
from pymongo.errors import OperationFailure
from pymongo.errors import CollectionInvalid




'''
' myInfo包含连接mongodb的基本配置信息
' ip : mongodb所在ip
' port : mongodb配置的端口号
' user : 认证所需的用户名
' password: 认证所需的密码
' 使用时需修改ip和端口号为你的mongodb的ip和端口
'.若你的mongodb开启了认证，则需修改用户名和密码
'''
myInfo = {
    "ip" : '10.0.86.201',
    "port" : 27017,
    "user" : "admin",
    "password" : "admin"
}


class MongoTest(object):

    def __init__(self):
        '''
        'connect   与mongodb的连接
        'db        当前连接下所使用的数据库
        '''
        #连接到mongodb
        try:
            self.connect = MongoClient(myInfo["ip"], myInfo["port"])
            self.connect.admin.command('ismaster')   #执行简单命令判断是否连接成功
        except ConnectionFailure:
            print("Server not available!")
            sys.exit()
        #进行用户认证（默认不需认证，若需认证，可将下面代码段的注释符删去，即可完成认证）
        '''
        try:
            self.db = self.connect.admin
            self.db.authenticate(myInfo["user"], myInfo["password"])
        except OperationFailure:
            print("Authentication failed!")
            sys.exit()
        '''




    def createCollection(self, database, coll):
        '''
        '在指定数据库中新建集合
        '若数据库已存在，则直接在其中新建集合
        '若该数据库不存在，则先新建这个数据库，并在其中新建集合
        '若数据库中该集合已经存在，则创建失败
        '
        '参数说明：
        'database  数据库名  string
        'coll      集合名    string
        '''
        db = self.connect.get_database(database)
        try:
            db.create_collection(coll)
            print("successfully created a collection!")
        except CollectionInvalid: #若集合已存在
            print("create collection failed, please check your collection name!")  




    def deleteCollection(self, database, coll):
        '''
        '删除指定数据库中的集合
        '若数据库，集合均存在，则删除成功
        '若数据库或者集合不存在，则删除失败
        '
        '参数说明：
        'database  数据库名  string
        'coll      集合名    string
        '''
        db = self.connect.get_database(database)
        message = db.drop_collection(coll)
        if message['ok'] == 1 :
            print("successfully droped collection!")
        else:
            print("delete collection failed, please check your database and collection name!")




    def deleteDatabase(self, database):
        '''
        '删除mongodb中指定的数据库
        '无论指定的数据库是否存在，pymongo的drop_database()均认为删除成功，不会返回任何提示信息
        '
        '参数说明：
        'database  数据库名  string
        '''
        self.connect.drop_database(database)
        print("successfully droped database!")




    def insert(self, database, coll, dic):
        '''
        '向指定数据库与集合中插入一个文档
        '若数据库或者集合不存在，则会先新建数据库或集合，然后再插入文档
        '
        '参数说明
        'database  数据库名  string
        'coll      集合名    string
        'dic       文档      dictionary
        '''
        db = self.connect.get_database(database)
        c = db.get_collection(coll)
        c.insert_one(dic)
        print("insert successfully!")




    def update(self, database, coll, filterdic, updatedic):
        '''
        '修改指定数据库与集合中的符合过滤条件的文档
        '若指定数据库或集合不存在，则mongodb将不做任何修改
        '若无符合过滤条件的文档，则mongodb将不做任何修改
        '若有符合过滤条件的文档，但想要使用$set修改的字段不存在,则会将该字段加入到符合过滤条件的所有文档中
        '
        '参数说明
        'database  数据库名  string
        'coll      集合名    string
        'filterdic 过滤条件  dictionary
        'updatedic.修改内容  dictionary
        '''
        db = self.connect.get_database(database)
        c = db.get_collection(coll)
        if c.count_documents(filterdic) == 0:  #判断符合查询条件的文档数是否为0
            print("No this collection or the collection is empty or no qualified docs!")
        else:
            c.update_many(filterdic, updatedic)
            print("update successfully!")




    def delete(self, database, coll, filterdic):
        '''
        '删除指定数据库与集合中的符合过滤条件的文档
        '若指定数据库或集合不存在，则mongodb将不做任何修改
        '若无符合过滤条件的文档，则mongodb将不做任何修改
        '
        '参数说明
        'database  数据库名  string
        'coll      集合名    string
        'filterdic 过滤条件  dictionary
        '''
        db = self.connect.get_database(database)
        c = db.get_collection(coll)
        if c.count_documents(filterdic) == 0:  #判断符合条件的文档数是否为0
            print("No this collection or the collection is empty or no qualified docs!")
        else:
            c.delete_many(filterdic)
            print("delete successfully!")




    def query(self, database, coll, filterdic):
        '''
        '从指定数据库与集合中查询符合过滤条件的文档
        '若指定数据库或集合不存在，则查询结果为空
        '若无符合过滤条件的文档，则查询结果为空
        '
        '参数说明
        'database  数据库名  string
        'coll      集合名    string
        'filterdic 过滤条件  dictionary
        '''
        db = self.connect.get_database(database)
        c = db.get_collection(coll)
        query_result = c.find(filterdic)  #mongodb返回的查询结果集合是一个cursor对象
        if query_result.collection.count_documents({}) == 0:  #通过cursor.collection.count_documents()可得到结果集中的全部文档数
            print("No qualified results!")
        else:
            print("the query results are as follows:")
            for r in query_result:
                print(r)




    def findAll(self, database, coll):
        '''
        '查询指定数据库与集合中的全部文档
        '若指定数据库或集合不存在，或集合为空，则查询结果为空
        '
        '参数说明
        'database  数据库名  string
        'coll      集合名    string
        '''
        db = self.connect.get_database(database)
        c = db.get_collection(coll)
        all_result = c.find()  #mongodb返回的查询结果集合是一个cursor对象
        if all_result.collection.count_documents({}) == 0:  #通过cursor.collection.count_documents()可得到结果集中的全部文档数
            print("No this collection or the collection is empty")
        else:
            print("all the docs in this collection are as follows:")
            for i in all_result:
                print(i)




    def sort(self, database, coll, sort_field, order):
        '''
        '对指定数据库与集合中的全部文档进行排序
        '若指定数据库或集合不存在，或集合为空，则无排序结果
        '若排序的关键字段在该集合中不存在，则返回集合中所有文档，不进行排序操作
        '
        '参数说明
        'database    数据库名        string
        'coll        集合名          string
        'sort_field  排序使用的字段  key or list
        'order       排序次序        默认升序，升序指定方式（1或者pymongo.ASCENDING），降序指定方式（-1或者pymongo.DESCENDING）
        '''
        db = self.connect.get_database(database)
        c = db.get_collection(coll)
        r = c.find()  #mongodb返回的查询结果集合是一个cursor对象
        if r.collection.count_documents({}) == 0:  #通过cursor.collection.count_documents()可得到结果集中的全部文档数
            print("No this collection or the collection is empty")
        else:
            print("the sorted docs are as follows:")
            for i in r.sort(sort_field, order):
                print(i)




    def close(self):
        '''
        '关闭与mongodb的连接
        '''
        self.connect.close()




def main():
    '''
    '对api进行测试
    '''
    #连接到mongodb
    client = MongoTest()

    #创建数据库和集合
    #数据库名为testdb1
    #集合名为collection1
    client.createCollection("testdb1", "collection1")

    #向数据库testdb1的集合collection1中插入两个文档
    doc1 = {"name":"a", "year":2018}
    client.insert("testdb1", "collection1", doc1)
    doc2 = {"name":"b", "year":2017}
    client.insert("testdb1", "collection1", doc2)

    #查询数据库testdb1的集合collection1中的全部文档
    client.findAll("testdb1", "collection1")

    #查询数据库testdb1的集合collection1中符合条件的文档
    query_filter = {"name":"a"}  #查询条件
    client.query("testdb1", "collection1", query_filter)

    #对数据库testdb1的集合collection1中符合条件的文档进行修改
    update_filter = {"year":2017}  #需满足的条件
    set_value = {"$set":{"name":"e"}}  #使用mongodb中的$set关键字对指定字段进行修改
    client.update("testdb1", "collection1", update_filter, set_value)

    #对数据库testdb1的集合collection1中的全部文档进行排序
    sort_field = "year"  #排序的关键字段
    order = 1  # 设置排序次序为升序，若降序则order = -1
    #或者使用order = pymongo.ASCENDING 或者 order = pymongo.DESCENDING
    client.sort("testdb1", "collection1", sort_field, order)

    #删除数据库testdb1的集合collection1中符合条件的文档
    delete_filter = {"name": "e"}  #删除需满足的条件
    client.delete("testdb1", "collection1", delete_filter)

    #删除数据库testdb1中的一个集合collection1
    client.deleteCollection("testdb1", "collection1")

    #删除一个数据库testdb1
    client.deleteDatabase("testdb1")
    
    #关闭连接
    client.close()
    





if __name__ == '__main__':
    main()
