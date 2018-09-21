##  scan_directory  
### 1 文件说明  
* scanDirPath.py  含主方法 main(), 扫描给定目录，对目录进行处理，将子目录和文件的元数据存储到 mongodb 中  
* collection.py   定义 mongodb 中 collection 的字段，字段详细解释参见 ../mongodb_doc_field.md
* function.py     定义若干函数，供 scanDirPath.py 中调用  

### 2 使用说明  
* **设置待扫描的目录**  
 在 scanDirPath.py 的 main() 方法中修改变量 dir_path 的值，将其改为待扫描的目录路径  
 
* **设置mongodb 连接信息**  
 在 scanDirPath.py 的 main() 方法中修改 connect() 方法中的参数的值，三个参数分别代表 数据库名，ip，端口
 
* **设置文件覆盖模式**  
 当多次扫描，扫描到同一目录下相同文件时覆盖或是跳过  
 在 scanDirPath.py 的 main() 方法中修改 cover_mode 值，True 代表覆盖，False 代表跳过  
 
* **设置系统模式**  
 当前待扫描目录所在的操作系统（便于扫描时过滤掉系统文件）  
 在 scanDirPath.py 的 main() 方法中修改 system_mode 值，1代表windows，2代表linux  
 
* **设置跳过文件**  
 将扫描时要跳过的文件的文件名添加到列表中  
 在 scanDirPath.py 中修改 break_names 的值  
 
* **设置 mongodb 中集合的名字**  
 需修改 collection.py 中的类名，当前为 user_bucket  
 同时需相应地修改 scanDirPath.py 和 function.py 中出现的 user_bucket  
 
