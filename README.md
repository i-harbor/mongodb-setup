##  mongodb   
###  1 mongotest.py
 mongotest.py 是使用 Python 连接 Mongodb, 并对 Mongodb 执行操作。

#### 1.1 建议版本
* python  3.7.0  
* mongodb  4.0.2  
* pymongo  3.7.1  

#### 1.2 说明
 mongotest.py 中所用API均为pymongo 3.7.1版本的API，详细可查阅官方API说明文档 http://api.mongodb.com/python/current/api/index.html  
 
### 2 mongodb_doc_field.md  
 我们使用mongodb来存储文件和目录的元数据，mongodb_doc_field.md 是对database，collection，document 的说明，对 document 中的每个字段 field 进行了详细的说明。
 
####  2.1 说明  
 字段 field 的类型我们采用了 mongoengine 中的 field 类型，具体可参见 mongoengine 的官方说明文档 http://docs.mongoengine.org/guide/defining-documents.html#fields  
 
### 3 scan_directory  
  scan_directory 是通过扫描目录，将目录下的所有文件和子目录的元数据都存储到 mongodb 中，具体说明可参见 scan_directory 目录下的readme文档。  

### 4 rados_io_test  
  rados_io_test 是对 rados 对象读写进行测试，具体说明可参见 rados_io_test 目录下的 readme 文档。  
 

 
