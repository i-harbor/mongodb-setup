## MongoDB shard集群 安全认证  

对于 MongoDB 中已经部署好的 shard 集群+副本集，启动安全认证，同时进行用户权限控制 

在配置过程中，集群需要 shutdown 一段时间  

### MongoDB 中的安全机制  
  
MongoDB 支持两种认证机制：  
+ SCRAM（默认机制）  
+ x.509 证书  

SCRAM：基于IETF标准（RFC 5802），进行认证时需要 用户名、密码、待访问的数据库  
x.509 证书：基于证书，建立 TLS/SSL 加密连接，多用于内部认证

### shard 集群+副本集安全认证简述   
  
shard 集群的安全认证分为两部分： 
+ 内部认证  
+ 基于角色的权限控制  
  
#### 内部认证  
内部认证是指 Mongo 集群内部节点之间进行访问的认证方式，如副本集内主备节点之间的访问、shard 集群内 Mongos 与 Mongod 之间的访问，它有两种方式：  
1. keyfile  
密钥文件方式，采用 SCRAM-SHA-1 机制，文件内包含了一个共享密钥，由集群内所有成员共同持有。通常，密钥的长度在6-1024字符内，采用 Base64 编码  
2. x.509 证书  
证书方式，集群中每一个实例彼此连接时都需要检验彼此使用的证书的内容是否相同，只有证书相同的实例彼此才能进行访问  

*注：x.509 证书的配置较为复杂，在本文档中使用 keyfile 的内部认证方式*

#### 基于角色的权限控制  
基于角色的权限控制通过角色赋予用户权限，授予用户一个或多个角色，以确定用户对数据库资源和操作的访问权限。这种认证方式常用于 MongoDB 单节点，或用于集群中 client 端连接 mongos 端  

MongoDB 中提供了诸多角色，具体可参见官方手册 https://docs.mongodb.com/manual/reference/built-in-roles/   

*注：如进行内部认证，则必须也进行用户权限控制* 

### shard 集群环境  
共3台服务器，分为3个 shard，每个 shard 都进行副本集配置（1主节点 + 1备节点 + 1仲裁节点）  
***
操作系统：CentOS7.0 64bit    
MongoDB 版本：mongodb-linux-x86_64-rhel70-4.0.3.tgz  
3台服务器 10.0.86.206，10.0.86.204，10.0.86.195  
***  
服务器规划：

|10.0.86.206|10.0.86.204|10.0.86.195|
|:-:|:-:|:-:|
|mongos|mongos|mongos|
|config|config|config|
|shard1主节点|shard2主节点|shard3主节点|
|shard3副节点|shard1副节点|shard2副节点|
|shard2仲节点|shard3仲节点|shard1仲节点|

端口分配：
```    
mongos:20000
config:21000
shard1:27001
shard2:27002
shard3:27003
```
*注：集群具体配置过程不再赘述，参见 https://github.com/evobstore/mongodb/blob/master/mongodb集群%2B分片部署.md*  

### 安全认证配置过程  

#### 1.创建 keyfile
连接到一台服务器，如10.0.86.206
```  
创建 keyfile 的存放目录
# mkdir /etc/mongodb
在该目录下生成 keyfile，命名为 keyfile0
# openssl rand -base64 756 > /etc/mongodb/keyfile0
设置只读权限
# chmod 400 /etc/mongodb/keyfile0
```  
将 keyfile0 复制到另外两台服务器的 /etc/mongodb 目录下  
同样设置只读权限  

#### 2.关闭 balancer  
连接到一台服务器，如10.0.86.206  
```
连接到 mongos
# mongo --port 20000
进入 mongos shell界面，关闭 balancer
sh.stopBalancer()
确认 balancer 是否完全关闭
sh.getBalancerState()
若返回 false，则 balancer 已关闭
```  
*注：balancer 关闭可能需要一段时间，必须等待 balancer 完全关闭后再进行后续操作*  
#### 3.关闭集群中所有的  mongos 实例  
逐一连接到每一个 mongos 实例，将其关闭  
连接到10.0.86.206  
```
连接到 mongos 
# mongo --port 20000
进入 mongos shell界面，执行关闭命令
db.getSiblingDB("admin").shutdownServer()
```
连接到10.0.86.204  
```
连接到 mongos 
# mongo --port 20000
进入 mongos shell界面，执行关闭命令
db.getSiblingDB("admin").shutdownServer()
```
连接到10.0.86.195  
```
连接到 mongos 
# mongo --port 20000
进入 mongos shell界面，执行关闭命令
db.getSiblingDB("admin").shutdownServer()
```

#### 4.关闭集群中所有 config server 的 mongod 实例  
逐一连接到 config server 的每一个 mongod 实例，将其关闭  
**特别注意：由于 config server 被部署为副本集，关闭时须最后关闭主节点**

在本环境中 10.0.86.206 为 config server 的主节点  

连接到10.0.86.204  
```
连接到 config 的 mongod
# mongo --port 21000
进入 shell 界面，执行关闭命令
db.getSiblingDB("admin").shutdownServer()
```
连接到10.0.86.195  
```
连接到 config 的 mongod
# mongo --port 21000
进入 shell 界面，执行关闭命令
db.getSiblingDB("admin").shutdownServer()
```
连接到10.0.86.206  
```
连接到 config 的 mongod
# mongo --port 21000
进入 shell 界面，执行关闭命令
db.getSiblingDB("admin").shutdownServer()
注：主节点的db.getSiblingDB("admin").shutdownServer()命令可能需要执行两次，第一次执行后从 primary 变为 secondary，第二次执行后成功关闭，视情况定
```

#### 5.关闭所有 shard 及其副本集的 mongod 实例  
逐一连接到每一个 shard 的每一个 mongod 实例，将其关闭 
同样需最后关闭副本集的主节点  

关闭 shard1 的 mongod 实例
```
连接到10.0.86.204
# mongo --port 27001
进入 shell 界面
db.getSiblingDB("admin").shutdownServer()
连接到10.0.86.195
# mongo --port 27001
进入 shell 界面
db.getSiblingDB("admin").shutdownServer()
连接到10.0.86.206
# mongo --port 27001
进入 shell 界面
db.getSiblingDB("admin").shutdownServer()
注：主节点的关闭命令可能需执行两次
```

关闭 shard2 的 mongod 实例
```
连接到10.0.86.206
# mongo --port 27002
进入 shell 界面
db.getSiblingDB("admin").shutdownServer()
连接到10.0.86.195
# mongo --port 27002
进入 shell 界面
db.getSiblingDB("admin").shutdownServer()
连接到10.0.86.204
# mongo --port 27002
进入 shell 界面
db.getSiblingDB("admin").shutdownServer()
注：主节点的关闭命令可能需执行两次
```

关闭 shard3 的 mongod 实例
```
连接到10.0.86.204
# mongo --port 27003
进入 shell 界面
db.getSiblingDB("admin").shutdownServer()
连接到10.0.86.206
# mongo --port 27003
进入 shell 界面
db.getSiblingDB("admin").shutdownServer()
连接到10.0.86.195
# mongo --port 27003
进入 shell 界面
db.getSiblingDB("admin").shutdownServer()
注：主节点的关闭命令可能需执行两次
```

#### 6.对 config server 进行内部安全认证   
对于 config server 的每个节点，修改配置文件，再进行重启  

连接到10.0.86.206
```
修改配置文件
# vim /usr/local/mongodb/conf/config.conf
在文件中增加内容
security:
  keyFile: /etc/mongodb/keyfile0
保存后重启 config server
# mongod -f /usr/local/mongodb/conf/config.conf
```
连接到10.0.86.204
```
修改配置文件
# vim /usr/local/mongodb/conf/config.conf
在文件中增加内容
security:
  keyFile: /etc/mongodb/keyfile0
保存后重启 config server
# mongod -f /usr/local/mongodb/conf/config.conf
```
连接到10.0.86.195
```
修改配置文件
# vim /usr/local/mongodb/conf/config.conf
在文件中增加内容
security:
  keyFile: /etc/mongodb/keyfile0
保存后重启 config server
# mongod -f /usr/local/mongodb/conf/config.conf
```  

#### 7.对 shard 进行内部安全认证
对于每个 shard 的每个节点，修改配置文件，再进行重启  

连接到10.0.86.206
```
修改 shard1 配置文件
# vim /usr/local/mongodb/conf/shard1.conf
在文件中增加内容
security:
  keyFile: /etc/mongodb/keyfile0
修改 shard2 配置文件
# vim /usr/local/mongodb/conf/shard2.conf
在文件中增加内容
security:
  keyFile: /etc/mongodb/keyfile0
修改 shard3 配置文件
# vim /usr/local/mongodb/conf/shard3.conf
在文件中增加内容
security:
  keyFile: /etc/mongodb/keyfile0
重启
# mongod -f /usr/local/mongodb/conf/shard1.conf
# mongod -f /usr/local/mongodb/conf/shard2.conf
# mongod -f /usr/local/mongodb/conf/shard3.conf
```
连接到10.0.86.204
```
修改 shard1 配置文件
# vim /usr/local/mongodb/conf/shard1.conf
在文件中增加内容
security:
  keyFile: /etc/mongodb/keyfile0
修改 shard2 配置文件
# vim /usr/local/mongodb/conf/shard2.conf
在文件中增加内容
security:
  keyFile: /etc/mongodb/keyfile0
修改 shard3 配置文件
# vim /usr/local/mongodb/conf/shard3.conf
在文件中增加内容
security:
  keyFile: /etc/mongodb/keyfile0
重启
# mongod -f /usr/local/mongodb/conf/shard1.conf
# mongod -f /usr/local/mongodb/conf/shard2.conf
# mongod -f /usr/local/mongodb/conf/shard3.conf
```
连接到10.0.86.195
```
修改 shard1 配置文件
# vim /usr/local/mongodb/conf/shard1.conf
在文件中增加内容
security:
  keyFile: /etc/mongodb/keyfile0
修改 shard2 配置文件
# vim /usr/local/mongodb/conf/shard2.conf
在文件中增加内容
security:
  keyFile: /etc/mongodb/keyfile0
修改 shard3 配置文件
# vim /usr/local/mongodb/conf/shard3.conf
在文件中增加内容
security:
  keyFile: /etc/mongodb/keyfile0
重启
# mongod -f /usr/local/mongodb/conf/shard1.conf
# mongod -f /usr/local/mongodb/conf/shard2.conf
# mongod -f /usr/local/mongodb/conf/shard3.conf
```

#### 8.对 mongos 进行内部安全认证  
对 mongos 的每个节点，修改配置文件，再进行重启  

连接到10.0.86.206
```
修改配置文件
# vim /usr/local/mongodb/conf/mongos.conf
在文件中增加内容
security:
  keyFile: /etc/mongodb/keyfile0
重启
# mongos -f /usr/local/mongodb/conf/mongos.conf
```
连接到10.0.86.204
```
修改配置文件
# vim /usr/local/mongodb/conf/mongos.conf
在文件中增加内容
security:
  keyFile: /etc/mongodb/keyfile0
重启
# mongos -f /usr/local/mongodb/conf/mongos.conf
```
连接到10.0.86.195
```
修改配置文件
# vim /usr/local/mongodb/conf/mongos.conf
在文件中增加内容
security:
  keyFile: /etc/mongodb/keyfile0
重启
# mongos -f /usr/local/mongodb/conf/mongos.conf
```

**至此，内部安全认证配置完毕， 下面进行基于角色的用户权限配置**
#### 9.用户权限配置  
连接到某一台 mongos，完成如下配置，如10.0.86.206  
```
# mongo --port 20000
```

创建用户管理员（可管理所有数据库的用户）
```
在 mongos shell 中执行
admin = db.getSiblingDB("admin")
admin.createUser(
  {
    user: "admin",
    pwd: "admin",
    roles: [ { role: "userAdminAnyDatabase", db: "admin" } ]
  }
)
```
认证为用户管理员
```
db.getSiblingDB("admin").auth("admin", "admin" )
```
创建集群管理员(可对整个集群进行管理)
```
db.getSiblingDB("admin").createUser(
  {
    "user" : "cluster",
    "pwd" : "cluster",
    roles: [ { "role" : "clusterAdmin", "db" : "admin" } ]
  }
)
```
认证为集群管理员
```
db.getSiblingDB("admin").auth("cluster", "cluster" )
```
重新启动 balancer
```
sh.startBalancer()
查看balancer状态 
sh.getBalancerState() 
若返回true，则启动成功
```
重新认证为用户管理员,再添加其他用户角色
```
db.getSiblingDB("admin").auth("admin", "admin" )
```
如：添加几个dbOwner用户（拥有该数据库最高权限）  
*注：用户在哪个数据库下创建，认证时就需要到那个数据库进行，因而创建时需先切换数据库*
```
切换数据库
use admin
创建超级用户
db.createUser(
  {
    "user" : "root",
    "pwd" : "root",
    roles: [ { "role" : "root", "db" : "admin" } ]
  }
)
切换数据库
use wjt
创建用户
db.createUser(
  {
    "user" : "wjt",
    "pwd" : "wjt",
    roles: [ { "role" : "dbOwner", "db" : "wjt" } ]
  }
)
切换数据库
use wys
创建用户
db.createUser(
  {
    "user" : "wys",
    "pwd" : "wys",
    roles: [ { "role" : "dbOwner", "db" : "wys" } ]
  }
)
切换数据库
use lyt
创建用户
db.createUser(
  {
    "user" : "lyt",
    "pwd" : "lyt",
    roles: [ { "role" : "dbOwner", "db" : "lyt" } ]
  }
)
```
查看所有用户
```
db.system.users.find().pretty()
```
**至此，基于角色的用户权限配置完毕**  

#### 附：在连接 shard 集群时，进行用户认证的两种方式    
1. 连接 mongos 时即进行认证  
```
# mongo --port 20000 -u "wjt" -p "wjt" --authenticationDatabase "wjt"
```
2. 先连接 mongos ，再认证
```
# mongo --port 20000
在 mongos shell 界面下
use wjt
db.auth('wjt','wjt')
```

#### 补充说明  
按照上述方式添加配置的用户角色只能在任意 mongos 和 config servers 的 mongod 实例上登录，不能在 shard 分片的 mongod 上进行登录，若登录将提示认证失败 

**原因是集群用户不能直接认证到某个 shard 的某个节点，shard 节点需单独创建用户**   

在某个 shard 节点上创建的用户称为 Shard Local Users，它和通过 mongos 创建的用户是完全独立的，Shard Local Users 只能在自己的 shard 上进行认证，不能在 mongos 上进行认证  

另外，对于副本集而言，不能在仲裁节点(arbiter)上创建或认证用户  

因此，如需直接在某个 shard 的节点上执行需要认证的命令，可使用如下方式：  
```
连接到 shard1 的主节点（10.0.86.206）
mongo --port 27001
进入mongo shell界面后，执行
db.getSiblingDB("admin").createUser(
  {
    "user" : "root",
    "pwd" : "root",
    roles: [ { "role" : "root", "db" : "admin" } ]
  }
)
可在 shard1 上成功创建超级用户
认证用户
use admin
db.auth('root','root')
获取状态
db.serverStatus()
```


