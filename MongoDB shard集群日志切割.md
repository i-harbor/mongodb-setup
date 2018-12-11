## MongoDB shard集群 日志切割  

对于 MongoDB shard集群而言，连接到任一 mongos 或 mongod 实例的操作，其详细信息都将被记录到日志中   

而 MongoDB 不会自动地进行日志切割，所有日志记录将持续写入一个文件，导致日志文件越来越大，不仅占用大量磁盘空间、降低写入性能，同时也为日志管理带来困难   

MongoDB 提供了 Rotate 方法，以进行日志切割  

*说明：本文中的所有日志均指 MongoDB 的系统日志 systemLog，而非 journal 等日志*  

### MongoDB 的日志机制简述  

#### 配置文件

MongoDB 日志机制的实现主要体现在其配置文件中，需对 systemLog 项进行相应配置  

```
systemLog:
   verbosity: <int>
   quiet: <boolean>
   traceAllExceptions: <boolean>
   syslogFacility: <string>
   path: <string>
   logAppend: <boolean>
   logRotate: <string>
   destination: <string>
   timeStampFormat: <string>
   component:
      accessControl:
         verbosity: <int>
      command:
         verbosity: <int>
```

对于 destination 项，若不进行指定，则日志将输出到标准输出，若进行指定，可指定为 file 或 syslog    
若指定为 file，则需配置 path 项，即日志文件的存放路径  

*注：以下只讨论 destination 指定为 file 的情况，即只考虑日志文件的切割，syslog 和 标准输出的情景不再考虑*  

对于 logRotate 项，即日志切割方式，有两种设置： 
+ rename  
+ reopen  

若不进行该项配置，则默认使用 rename 方式  
rename 将原日志文件重命名为“文件名+时间戳”，新建一个日志文件，后续日志均写入新文件  
reopen 使用 Linux/Unix 系统的 logRotate 工具来切割，日志文件需要外部进程来重命名  

*注：我们使用默认的 rename 方式，对于 reopen 的使用方法不再讨论*

#### 实现日志切割  
MongoDB 不会自动地进行日志切割，只有当接收到 logRotate 命令，或 mongod/mongos 进程接收到操作系统的 SIGUSR1 信号，才会执行日志切割操作  

因此，实现日志切割的两种方式：  
+ 在 mongo shell 中执行 logRotate 命令  
+ 通过sh脚本向 mongod 和 mongos 进程发送 SIGUSR1 信号 

***
### shard 集群环境  
共3台服务器，分为3个 shard，每个 shard 都进行副本集配置（1主节点 + 1备节点 + 1仲裁节点）  

操作系统：CentOS7.0 64bit    
MongoDB 版本：mongodb-linux-x86_64-rhel70-4.0.3.tgz  
3台服务器 10.0.86.206，10.0.86.204，10.0.86.195  

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

***  
### 实现方式一：执行 logRotate 命令  
对于已经部署好的 shard 集群，由于 logRotate 默认为 rename，故不需要再  shutdown 集群修改配置文件重启，直接进行日志切割操作即可，方式二也是如此。  

由于 logRoate 命令需在 mongo shell 中执行，故需细分为两种情况：  
+ 集群未进行安全认证  
+ 集群已完成安全认证  

#### 若集群未进行安全认证配置   
需连接到每一台服务器，对其上所有 mongod 和 mongos 实例，进入到 shell，执行 logRotate 命令  

以 10.0.86.206 为例  

```
连接到 mongos 
# mongo --port 20000
进入 mongos shell界面，执行切割命令
db.adminCommand( { logRotate : 1 } )

连接到 config 的 mongod
# mongo --port 21000
进入 mongos shell界面，执行切割命令
db.adminCommand( { logRotate : 1 } )

连接到 shard1 的 mongod
# mongo --port 27001
进入 mongos shell界面，执行切割命令
db.adminCommand( { logRotate : 1 } )

连接到 shard2 的 mongod
# mongo --port 27002
进入 mongos shell界面，执行切割命令
db.adminCommand( { logRotate : 1 } )

连接到 shard3 的 mongod
# mongo --port 27003
进入 mongos shell界面，执行切割命令
db.adminCommand( { logRotate : 1 } )
```

其它两台服务器同样执行上述操作，此处不再赘述  

#### 若集群已完成安全认证配置   
*注：集群安全认证配置参见 https://github.com/evobstore/Docs/blob/master/MongoDB%20shard集群安全认证.md*  

logRoate 命令需有相应权限才能成功执行  
若集群中无 root 超级用户，建议创建 root 用户，以 root 身份执行 logRotate 命令  

创建 root 用户  

连接到某一台 mongos，完成如下配置，如10.0.86.206
```
# mongo --port 20000

以用户管理员身份登录
use admin
db.auth('admin','admin')

在 admin 下创建超级用户 root
use admin
db.createUser(
  {
    "user" : "root",
    "pwd" : "root",
    roles: [ { "role" : "root", "db" : "admin" } ]
  }
)
```

再分别连接到每一台服务器，对其上所有 mongod 和 mongos 实例，进入到 shell，以 root 身份登录，执行 logRotate 命令  

以 10.0.86.206 为例
```
连接到 mongos 
# mongo --port 20000
以 root 身份登录
use admin
db.auth('root','root')
执行切割命令
db.adminCommand( { logRotate : 1 } )

连接到 config 的 mongod
# mongo --port 21000
以 root 身份登录
use admin
db.auth('root','root')
执行切割命令
db.adminCommand( { logRotate : 1 } )

连接到 shard1 的 mongod
# mongo --port 27001
以 root 身份登录
use admin
db.auth('root','root')
执行切割命令
db.adminCommand( { logRotate : 1 } )

连接到 shard2 的 mongod
# mongo --port 27002
以 root 身份登录
use admin
db.auth('root','root')
执行切割命令
db.adminCommand( { logRotate : 1 } )

连接到 shard3 的 mongod
# mongo --port 27003
以 root 身份登录
use admin
db.auth('root','root')
执行切割命令
db.adminCommand( { logRotate : 1 } )
```

其它两台服务器同样执行上述操作，此处不再赘述  

***

### 实现方式二：发送  SIGUSR1 信号  
此方式通过编写sh脚本，向服务器上所有 mongod 和 mongos 进程发送 SIGUSR1 信号完成日志切割，无需进行认证，同时可设置定时任务  

连接到每一台服务器，执行如下操作，以 10.0.86.206 为例
```
在 root 目录下创建sh脚本
# vim /root/logrotate.sh

在脚本中写入如下内容：
#!/bin/bash
#Rotate the MongoDB logs to prevent a single logfile from consuming too much disk space.

app1=mongod
app2=mongos

mongoPath=/usr/local/mongodb/bin/

pidArray1=$(pidof $mongoPath/$app1)
pidArray2=$(pidof $mongoPath/$app2)

for pid in $pidArray1;do
if [ $pid ]
then
    kill -SIGUSR1 $pid
fi
done

for pid in $pidArray2;do
if [ $pid ]
then
    kill -SIGUSR1 $pid
fi
done

exit

保存后退出
赋予脚本执行权限
# chmod +x logrotate.sh
执行脚本
./logrotate.sh

该服务器上的日志完成切割
```

其它两台服务器同样执行上述操作，此处不再赘述

#### 下面实现定时的日志切割：  
利用 Linux 上的 crontab 服务来完成定时日志切割，将上述的 logrotate.sh 添加到 crontab 的定时任务中即可  

例如：每天 23:59 进行日志切割  

连接到每一台服务器，进行如下操作，以 10.0.86.206 为例  

```
查看 crontab 服务状态，检查服务是否开启
/bin/systemctl status crond.service
若未开启，可执行
/bin/systemctl start crond.service

编辑文件
# vim /etc/crontab
在文件底部添加
59 23 * * * root /root/logrotate.sh
保存并退出

即可实现定时日志自动切割
```

其它两台服务器同样执行上述操作，此处不再赘述  

若需定时对日志进行清理，可通过在上述 logrotate.sh 文件 exit 语句上方添加如下语句实现  
```
logpath=/var/log/mongodb/
days=7

find $logpath -mtime +$days -delete
```

上例为清理距今超过7天的日志文件，故该脚本可完成日志切割和日志清理两个功能，若设置 crontab 定时任务，即可完成定时切割和清理   




