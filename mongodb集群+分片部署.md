
## MongoDB4.0.3集群搭建
根据对象存储平台Django+MongoDB+Ceph的需求，现搭建部署一个十节点的MongoDB集群，主要以下关键点： 

- 根据最新版本MongoDB推荐，配置文件采用yaml方式来配置
- 一共10台服务器，即10个节点。对数据集进行分片，共分10个shard
- 每一个shard都进行副本集配置，由于硬件磁盘已进行raid多副本备份，考虑到存储效率，本集群在副本集只需要一个备服务器，故采用1主+1备
+1仲裁（必须有仲裁节点，不然被服务器无法通过心跳机制升级为主服务器）的副本及配置方式

### 环境准备 
系统：CentOS7.0 64bit

十台服务器：mongo00-mongo09

服务器规划：

|mongo00|mongo01|mongo02|mongo03|mongo04|mongo05|mongo06|mongo07|mongo08|mongo09|
|-|-|-|-|-|-|-|-|-|-|
|mongos|mongos|mongos|mongos|mongos|mongos|mongos|config|config|config|
|shard0主|shard1主|shard2主|shard3主|shard4主|shard5主|shard6主|shard7主|shard8主|shard9主|
|shard9副|shard0副|shard1副|shard2副|shard3副|shard4副|shard5副|shard6副|shard7副|shard8副|
|shard8仲|shard9仲|shard0仲|shard1仲|shard2仲|shard3仲|shard4仲|shard5仲|shard6仲|shard7仲|

端口分配：
```
mongos:20000
config:21000
shard0:27000
shard1:27001
shard2:27002
shard3:27003
shard4:27004
shard5:27005
shard6:27006
shard7:27007
shard8:27008
shard9:27009
```

### MongoDB安装
1. 下载、安装MongoDB
```
#官网下载
wget https://fastdl.mongodb.org/linux/mongodb-linux-x86_64-rhel70-4.0.3.tgz

#解压
tar -xzvf mongodb-linux-x86_64-rhel70-4.0.3.tgz -C /usr/local/
cd /use/local
mv mongodb-linux-x86_64-rhel70-4.0.3 mongodb
```
2. 相关目录规划
```
#mongo服务通过配置文件启动,存放配置文件目录/usr/local/mongodb/conf
#存放日志、进程管理信息的目录/var/log/nginx/mongodb
#根据服务器规划，在每台服务器创建该节点所含shard的数据存放目录/mnt/mongodata/shard0-9
#同时在mongo07-mongo09三台服务器创建存放config server数据的数据目录/mnt/mongodata/config

#mongo00:
mkdir -p /usr/local/mongodb/conf
mkdir -p /var/log/nginx/mongodb
mkdir -p /mnt/mongodata/shard0
mkdir -p /mnt/mongodata/shard9
mkdir -p /mnt/mongodata/shard8

#mongo01:
mkdir -p /usr/local/mongodb/conf
mkdir -p /var/log/nginx/mongodb
mkdir -p /mnt/mongodata/shard0
mkdir -p /mnt/mongodata/shard1
mkdir -p /mnt/mongodata/shard9

#mongo02:
mkdir -p /usr/local/mongodb/conf
mkdir -p /var/log/nginx/mongodb
mkdir -p /mnt/mongodata/shard0
mkdir -p /mnt/mongodata/shard1
mkdir -p /mnt/mongodata/shard2

#mongo03:
mkdir -p /usr/local/mongodb/conf
mkdir -p /var/log/nginx/mongodb
mkdir -p /mnt/mongodata/shard1
mkdir -p /mnt/mongodata/shard2
mkdir -p /mnt/mongodata/shard3

#mongo04:
mkdir -p /usr/local/mongodb/conf
mkdir -p /var/log/nginx/mongodb
mkdir -p /mnt/mongodata/shard2
mkdir -p /mnt/mongodata/shard3
mkdir -p /mnt/mongodata/shard4

#mongo05:
mkdir -p /usr/local/mongodb/conf
mkdir -p /var/log/nginx/mongodb
mkdir -p /mnt/mongodata/shard3
mkdir -p /mnt/mongodata/shard4
mkdir -p /mnt/mongodata/shard5

#mongo06:
mkdir -p /usr/local/mongodb/conf
mkdir -p /var/log/nginx/mongodb
mkdir -p /mnt/mongodata/shard4
mkdir -p /mnt/mongodata/shard5
mkdir -p /mnt/mongodata/shard6

#mongo07:
mkdir -p /usr/local/mongodb/conf
mkdir -p /var/log/nginx/mongodb
mkdir -p /mnt/mongodata/shard5
mkdir -p /mnt/mongodata/shard6
mkdir -p /mnt/mongodata/shard7
mkdir -p /mnt/mongodata/config

#mongo08:
mkdir -p /usr/local/mongodb/conf
mkdir -p /var/log/nginx/mongodb
mkdir -p /mnt/mongodata/shard6
mkdir -p /mnt/mongodata/shard7
mkdir -p /mnt/mongodata/shard8
mkdir -p /mnt/mongodata/config

#mongo09:
mkdir -p /usr/local/mongodb/conf
mkdir -p /var/log/nginx/mongodb
mkdir -p /mnt/mongodata/shard7
mkdir -p /mnt/mongodata/shard8
mkdir -p /mnt/mongodata/shard9
mkdir -p /mnt/mongodata/config

```
3. 环境变量配置
```
vim /etc/profile

#加入以下内容
export MONGODB_HOME=/usr/local/mongodb
export PATH=$MONGODB_HOME/bin:$PATH

#立即生效
source /etc/profile
```
使用命令`mongod -v`输出信息版本信息验证环境变量是否配置成功

### 集群配置
#### 1、config server配置服务器（副本集）
根据服务器规划，在mongo07-mongo09上部署三台config server副本集，在该三台服务器上分别添加以下配置文件：
```
vim /usr/local/mongodb/conf/config.conf


# where to write logging data.
systemLog:
  destination: file
  logAppend: true
  path: /var/log/nginx/mongodb/config.log
 
# Where and how to store data.
storage:
  dbPath: /mnt/mongodata/config
  journal:
    enabled: true

# how the process runs
processManagement:
  fork: true
  pidFilePath: /var/log/nginx/mongodb/configsrv.pid
 
# network interfaces
net:
  port: 21000
  bindIp: 0.0.0.0
 
#operationProfiling:
replication:
    replSetName: configs       

sharding:
    clusterRole: configsvr

```
启动这三台服务器的config server
```
mongod -f /usr/local/mongodb/conf/config.conf
```
登陆任意一台服务器，初始化副本集
```
mongo --port 21000

#定义副本集配置（键“_id”对应的值必须与配置文件中的replicaction.replSetName一致）
config = {
...    _id : "configs",
...     members : [
...         {_id : 0, host : "mongo07:21000" },
...         {_id : 1, host : "mongo08:21000" },
...         {_id : 2, host : "mongo09:21000" }
...     ]
... }

#初始化副本集
rs.initiate(config)

#查看分区状态
rs.status();
```
#### 2、shard server分片服务器（副本集）

##### 配置shard0副本集
在mongo00、mongo01、mongo02服务器上做以下配置：
```
vim /usr/local/mongodb/conf/shard0.conf


# where to write logging data.
systemLog:
  destination: file
  logAppend: true
  path: /var/log/nginx/mongodb/shard0.log
 
# Where and how to store data.
storage:
  dbPath: /mnt/mongodata/shard0
  journal:
    enabled: true

# how the process runs
processManagement:
  fork: true
  pidFilePath: /var/log/nginx/mongodb/shard0.pid
 
# network interfaces
net:
  port: 27000
  bindIp: 0.0.0.0
 
#operationProfiling:
replication:
    replSetName: shard0       

sharding:
    clusterRole: shardsvr
```
启动这三台服务器的shard0 server
```
mongod -f /usr/local/mongodb/conf/shard0.conf
```
登陆任意一台服务器，初始化副本集
```
mongo --port 27000

#定义副本集配置（键“_id”对应的值必须与配置文件中的replicaction.replSetName一致,priority代表权重[1,100]，大的被分配为主服务器，0永久不会变为主服务器）
config = {
...    _id : "shard0",
...     members : [
...         {_id : 0, host : "mongo00:27000", priority : 2 },
...         {_id : 1, host : "mongo01:27000", priority : 1 },
...         {_id : 2, host : "mongo02:27000", arbiterOnly :true }
...     ]
... }

#初始化副本集
rs.initiate(config)

#查看分区状态
rs.status();
```

##### 配置shard1副本集
在mongo01、mongo02、mongo03服务器上做以下配置：
```
vim /usr/local/mongodb/conf/shard1.conf


# where to write logging data.
systemLog:
  destination: file
  logAppend: true
  path: /var/log/nginx/mongodb/shard1.log
 
# Where and how to store data.
storage:
  dbPath: /mnt/mongodata/shard1
  journal:
    enabled: true

# how the process runs
processManagement:
  fork: true
  pidFilePath: /var/log/nginx/mongodb/shard1.pid
 
# network interfaces
net:
  port: 27001
  bindIp: 0.0.0.0
 
#operationProfiling:
replication:
    replSetName: shard1

sharding:
    clusterRole: shardsvr
```
启动这三台服务器的shard1 server
```
mongod -f /usr/local/mongodb/conf/shard1.conf
```
登陆任意一台服务器，初始化副本集
```
mongo --port 27001

#定义副本集配置（键“_id”对应的值必须与配置文件中的replicaction.replSetName一致,priority代表权重[1,100]，大的被分配为主服务器，0永久不会变为主服务器）
config = {
...    _id : "shard1",
...     members : [
...         {_id : 0, host : "mongo01:27001", priority : 2 },
...         {_id : 1, host : "mongo02:27001", priority : 1 },
...         {_id : 2, host : "mongo03:27001", arbiterOnly :true }
...     ]
... }

#初始化副本集
rs.initiate(config)

#查看分区状态
rs.status();
```


##### 配置shard2副本集
在mongo02、mongo03、mongo04服务器上做以下配置：
```
vim /usr/local/mongodb/conf/shard2.conf


# where to write logging data.
systemLog:
  destination: file
  logAppend: true
  path: /var/log/nginx/mongodb/shard2.log
 
# Where and how to store data.
storage:
  dbPath: /mnt/mongodata/shard2
  journal:
    enabled: true

# how the process runs
processManagement:
  fork: true
  pidFilePath: /var/log/nginx/mongodb/shard2.pid
 
# network interfaces
net:
  port: 27002
  bindIp: 0.0.0.0
 
#operationProfiling:
replication:
    replSetName: shard2

sharding:
    clusterRole: shardsvr
```
启动这三台服务器的shard2 server
```
mongod -f /usr/local/mongodb/conf/shard2.conf
```
登陆任意一台服务器，初始化副本集
```
mongo --port 27002

#定义副本集配置（键“_id”对应的值必须与配置文件中的replicaction.replSetName一致,priority代表权重[1,100]，大的被分配为主服务器，0永久不会变为主服务器）
config = {
...    _id : "shard2",
...     members : [
...         {_id : 0, host : "mongo02:27002", priority : 2 },
...         {_id : 1, host : "mongo03:27002", priority : 1 },
...         {_id : 2, host : "mongo04:27002", arbiterOnly :true }
...     ]
... }

#初始化副本集
rs.initiate(config)

#查看分区状态
rs.status();
```

##### 配置shard3副本集
在mongo03、mongo04、mongo05服务器上做以下配置：
```
vim /usr/local/mongodb/conf/shard3.conf


# where to write logging data.
systemLog:
  destination: file
  logAppend: true
  path: /var/log/nginx/mongodb/shard3.log
 
# Where and how to store data.
storage:
  dbPath: /mnt/mongodata/shard3
  journal:
    enabled: true

# how the process runs
processManagement:
  fork: true
  pidFilePath: /var/log/nginx/mongodb/shard3.pid
 
# network interfaces
net:
  port: 27003
  bindIp: 0.0.0.0
 
#operationProfiling:
replication:
    replSetName: shard3

sharding:
    clusterRole: shardsvr
```
启动这三台服务器的shard3 server
```
mongod -f /usr/local/mongodb/conf/shard3.conf
```
登陆任意一台服务器，初始化副本集
```
mongo --port 27003

#定义副本集配置（键“_id”对应的值必须与配置文件中的replicaction.replSetName一致,priority代表权重[1,100]，大的被分配为主服务器，0永久不会变为主服务器）
config = {
...    _id : "shard3",
...     members : [
...         {_id : 0, host : "mongo03:27003", priority : 2 },
...         {_id : 1, host : "mongo04:27003", priority : 1 },
...         {_id : 2, host : "mongo05:27003", arbiterOnly :true }
...     ]
... }

#初始化副本集
rs.initiate(config)

#查看分区状态
rs.status();
```

##### 配置shard4副本集
在mongo04、mongo05、mongo06服务器上做以下配置：
```
vim /usr/local/mongodb/conf/shard4.conf


# where to write logging data.
systemLog:
  destination: file
  logAppend: true
  path: /var/log/nginx/mongodb/shard4.log
 
# Where and how to store data.
storage:
  dbPath: /mnt/mongodata/shard4
  journal:
    enabled: true

# how the process runs
processManagement:
  fork: true
  pidFilePath: /var/log/nginx/mongodb/shard4.pid
 
# network interfaces
net:
  port: 27004
  bindIp: 0.0.0.0
 
#operationProfiling:
replication:
    replSetName: shard4

sharding:
    clusterRole: shardsvr
```
启动这三台服务器的shard4 server
```
mongod -f /usr/local/mongodb/conf/shard4.conf
```
登陆任意一台服务器，初始化副本集
```
mongo --port 27004

#定义副本集配置（键“_id”对应的值必须与配置文件中的replicaction.replSetName一致,priority代表权重[1,100]，大的被分配为主服务器，0永久不会变为主服务器）
config = {
...    _id : "shard4",
...     members : [
...         {_id : 0, host : "mongo04:27004", priority : 2 },
...         {_id : 1, host : "mongo05:27004", priority : 1 },
...         {_id : 2, host : "mongo06:27004", arbiterOnly :true }
...     ]
... }

#初始化副本集
rs.initiate(config)

#查看分区状态
rs.status();
```

##### 配置shard5副本集
在mongo05、mongo06、mongo07服务器上做以下配置：
```
vim /usr/local/mongodb/conf/shard5.conf


# where to write logging data.
systemLog:
  destination: file
  logAppend: true
  path: /var/log/nginx/mongodb/shard5.log
 
# Where and how to store data.
storage:
  dbPath: /mnt/mongodata/shard5
  journal:
    enabled: true

# how the process runs
processManagement:
  fork: true
  pidFilePath: /var/log/nginx/mongodb/shard5.pid
 
# network interfaces
net:
  port: 27005
  bindIp: 0.0.0.0
 
#operationProfiling:
replication:
    replSetName: shard5

sharding:
    clusterRole: shardsvr
```
启动这三台服务器的shard5 server
```
mongod -f /usr/local/mongodb/conf/shard5.conf
```
登陆任意一台服务器，初始化副本集
```
mongo --port 27005

#定义副本集配置（键“_id”对应的值必须与配置文件中的replicaction.replSetName一致,priority代表权重[1,100]，大的被分配为主服务器，0永久不会变为主服务器）
config = {
...    _id : "shard5",
...     members : [
...         {_id : 0, host : "mongo05:27005", priority : 2 },
...         {_id : 1, host : "mongo06:27005", priority : 1 },
...         {_id : 2, host : "mongo07:27005", arbiterOnly :true }
...     ]
... }

#初始化副本集
rs.initiate(config)

#查看分区状态
rs.status();
```

##### 配置shard6副本集
在mongo06、mongo07、mongo08服务器上做以下配置：
```
vim /usr/local/mongodb/conf/shard6.conf


# where to write logging data.
systemLog:
  destination: file
  logAppend: true
  path: /var/log/nginx/mongodb/shard6.log
 
# Where and how to store data.
storage:
  dbPath: /mnt/mongodata/shard6
  journal:
    enabled: true

# how the process runs
processManagement:
  fork: true
  pidFilePath: /var/log/nginx/mongodb/shard6.pid
 
# network interfaces
net:
  port: 27006
  bindIp: 0.0.0.0
 
#operationProfiling:
replication:
    replSetName: shard6

sharding:
    clusterRole: shardsvr
```
启动这三台服务器的shard6 server
```
mongod -f /usr/local/mongodb/conf/shard6.conf
```
登陆任意一台服务器，初始化副本集
```
mongo --port 27006

#定义副本集配置（键“_id”对应的值必须与配置文件中的replicaction.replSetName一致,priority代表权重[1,100]，大的被分配为主服务器，0永久不会变为主服务器）
config = {
...    _id : "shard6",
...     members : [
...         {_id : 0, host : "mongo06:27006", priority : 2 },
...         {_id : 1, host : "mongo07:27006", priority : 1 },
...         {_id : 2, host : "mongo08:27006", arbiterOnly :true }
...     ]
... }

#初始化副本集
rs.initiate(config)

#查看分区状态
rs.status();
```

##### 配置shard7副本集
在mongo07、mongo08、mongo09服务器上做以下配置：
```
vim /usr/local/mongodb/conf/shard7.conf


# where to write logging data.
systemLog:
  destination: file
  logAppend: true
  path: /var/log/nginx/mongodb/shard7.log
 
# Where and how to store data.
storage:
  dbPath: /mnt/mongodata/shard7
  journal:
    enabled: true

# how the process runs
processManagement:
  fork: true
  pidFilePath: /var/log/nginx/mongodb/shard7.pid
 
# network interfaces
net:
  port: 27007
  bindIp: 0.0.0.0
 
#operationProfiling:
replication:
    replSetName: shard7

sharding:
    clusterRole: shardsvr
```
启动这三台服务器的shard7 server
```
mongod -f /usr/local/mongodb/conf/shard7.conf
```
登陆任意一台服务器，初始化副本集
```
mongo --port 27007

#定义副本集配置（键“_id”对应的值必须与配置文件中的replicaction.replSetName一致,priority代表权重[1,100]，大的被分配为主服务器，0永久不会变为主服务器）
config = {
...    _id : "shard7",
...     members : [
...         {_id : 0, host : "mongo07:27007", priority : 2 },
...         {_id : 1, host : "mongo08:27007", priority : 1 },
...         {_id : 2, host : "mongo09:27007", arbiterOnly :true }
...     ]
... }

#初始化副本集
rs.initiate(config)

#查看分区状态
rs.status();
```

##### 配置shard8副本集
在mongo08、mongo09、mongo00服务器上做以下配置：
```
vim /usr/local/mongodb/conf/shard8.conf


# where to write logging data.
systemLog:
  destination: file
  logAppend: true
  path: /var/log/nginx/mongodb/shard8.log
 
# Where and how to store data.
storage:
  dbPath: /mnt/mongodata/shard8
  journal:
    enabled: true

# how the process runs
processManagement:
  fork: true
  pidFilePath: /var/log/nginx/mongodb/shard8.pid
 
# network interfaces
net:
  port: 27008
  bindIp: 0.0.0.0
 
#operationProfiling:
replication:
    replSetName: shard8

sharding:
    clusterRole: shardsvr
```
启动这三台服务器的shard8 server
```
mongod -f /usr/local/mongodb/conf/shard8.conf
```
登陆任意一台服务器，初始化副本集
```
mongo --port 27008

#定义副本集配置（键“_id”对应的值必须与配置文件中的replicaction.replSetName一致,priority代表权重[1,100]，大的被分配为主服务器，0永久不会变为主服务器）
config = {
...    _id : "shard8",
...     members : [
...         {_id : 0, host : "mongo08:27008", priority : 2 },
...         {_id : 1, host : "mongo09:27008", priority : 1 },
...         {_id : 2, host : "mongo00:27008", arbiterOnly :true }
...     ]
... }

#初始化副本集
rs.initiate(config)

#查看分区状态
rs.status();
```

##### 配置shard9副本集
在mongo09、mongo00、mongo01服务器上做以下配置：
```
vim /usr/local/mongodb/conf/shard9.conf


# where to write logging data.
systemLog:
  destination: file
  logAppend: true
  path: /var/log/nginx/mongodb/shard9.log
 
# Where and how to store data.
storage:
  dbPath: /mnt/mongodata/shard9
  journal:
    enabled: true

# how the process runs
processManagement:
  fork: true
  pidFilePath: /var/log/nginx/mongodb/shard9.pid
 
# network interfaces
net:
  port: 27009
  bindIp: 0.0.0.0
 
#operationProfiling:
replication:
    replSetName: shard9

sharding:
    clusterRole: shardsvr
```
启动这三台服务器的shard9 server
```
mongod -f /usr/local/mongodb/conf/shard9.conf
```
登陆任意一台服务器，初始化副本集
```
mongo --port 27009

#定义副本集配置（键“_id”对应的值必须与配置文件中的replicaction.replSetName一致,priority代表权重[1,100]，大的被分配为主服务器，0永久不会变为主服务器）
config = {
...    _id : "shard9",
...     members : [
...         {_id : 0, host : "mongo09:27009", priority : 2 },
...         {_id : 1, host : "mongo00:27009", priority : 1 },
...         {_id : 2, host : "mongo01:27009", arbiterOnly :true }
...     ]
... }

#初始化副本集
rs.initiate(config)

#查看分区状态
rs.status();
```

#### 3、mongos server路由服务器（在mongo00-mongo06上配置）
>注意：启动mongodb时，先启动配置服务器和分片服务器，最后启动路由服务器

```
vim /usr/local/mongodb/conf/mongos.conf

systemLog:
  destination: file
  logAppend: true
  path: /var/log/nginx/mongodbmongos.log
processManagement:
  fork: true
#  pidFilePath: /var/log/nginx/mongodbmongos.pid
 
# network interfaces
net:
  port: 20000
  bindIp: 0.0.0.0
#监听的配置服务器,只能有1个或者3个 configs为配置服务器的副本集名字
sharding:
   configDB: configs/mongo07:21000,mongo08:21000,mongo09:21000
```
启动这七台服务器的mongos server
```
mongos -f /usr/local/mongodb/conf/mongos.conf
```

#### 4、启用分片
>目前已经搭建好配置服务器、数据分片服务器、路由服务器，下面进行分片启用，使得app连接到路由服务器时可以使用分片机制

登录任意一台mongos
```
mongo --port 20000

#使用admin数据库
use admin

#串联路由服务器与分片副本集
sh.addShard("shard0/mongo00:27000,mongo01:27000,mongo02:27000")
sh.addShard("shard1/mongo01:27001,mongo02:27001,mongo03:27001")
sh.addShard("shard2/mongo02:27002,mongo03:27002,mongo04:27002")
sh.addShard("shard3/mongo03:27003,mongo04:27003,mongo05:27003")
sh.addShard("shard4/mongo04:27004,mongo05:27004,mongo06:27004")
sh.addShard("shard5/mongo05:27005,mongo06:27005,mongo07:27005")
sh.addShard("shard6/mongo06:27006,mongo07:27006,mongo08:27006")
sh.addShard("shard7/mongo07:27007,mongo08:27007,mongo09:27007")
sh.addShard("shard8/mongo08:27008,mongo09:27008,mongo00:27008")
sh.addShard("shard9/mongo09:27009,mongo00:27009,mongo01:27009")

#查看集群状态
sh.status()
```





