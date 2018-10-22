##  rados_io_test  
### 1 文件说明  
* scanDirPathAndRados.py   含主方法 main(), 扫描给定目录,将子目录和文件的元数据存储到 mongodb 中, 并将文件以 rados 对象的形式存储到 ceph 集群中   
* collection.py            定义 mongodb 中 collection 的字段，即 mongoengine 的 module，字段详细解释参见 ../mongodb_doc_field.md  
* function.py              定义若干函数，供 scanDirPathAndRados.py 中调用    
* readRados.py             含主方法 main(), 给定文件名和文件路径，先到 mongodb 中获取元数据，再从 rados 读取相应对象    
* rados.so                 so动态库，含 rados 读写等接口，供.py 文件调用  

### 2 写 rados 使用说明    
* **设置待扫描的目录**  
 在 scanDirPathAndRados.py 的 main() 方法中修改变量 dir_path 的值，将其改为待扫描的目录路径  
 
* **设置 mongodb 连接信息**  
 在 scanDirPathAndRados.py 的 main() 方法中修改 connect() 方法中的参数的值，三个参数分别代表 数据库名，ip，端口
 
* **设置文件覆盖模式**  
 当多次扫描，扫描到同一目录下相同文件时覆盖或是跳过  
 在 scanDirPathAndRados.py 的 main() 方法中修改 cover_mode 值，True 代表覆盖，False 代表跳过  
 
* **设置系统模式**  
 当前待扫描目录所在的操作系统（便于扫描时过滤掉系统文件），建议2：linux  
 在 scanDirPathAndRados.py 的 main() 方法中修改 system_mode 值，1代表windows，2代表linux  
 
* **设置跳过文件**  
 将扫描时要跳过的文件的文件名添加到列表中  
 在 scanDirPathAndRados.py 中修改 break_names 的值  
 
* **设置 mongodb 中集合的名字**  
 需修改 function.py 中的变量：collection_name，当前为'bucket0'
 
### 3 读 rados 使用说明   
* **设置 mongodb 连接信息**  
在 readRados.py 的 main() 方法中修改 connect() 方法中的参数的值，三个参数分别代表 数据库名，ip，端口 

* **设置要读取的文件名**  
在 readRados.py 的 main() 方法中修改变量：filename，filedir

* **设置 mongodb 中集合的名字**   
需修改 function.py 中的变量：collection_name，当前为'bucket0'  


 
