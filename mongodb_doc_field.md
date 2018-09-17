##  mongodb中doc的字段设计

### 说明：
我们在mongodb中创建一个名为“metadata”的数据库，用于存放元数据。  
在该数据库下，我们为每个用户的每个bucket创建一个名为“username_bucketname”的collection。  

### document中字段设计如下表 ：  
|字段名|类型|说明|  
|:-----:|:---:|:---|  
|**na**|String|name，若该doc代表文件，则na为文件名，若该doc代表目录，则na为目录路径|  
|**fod**|Boolean|file_or_dir，用于判断该doc代表的是一个文件还是一个目录，若fod为True，则是文件，若fod为False，则是目录|  
|**did**|String|所在目录的objectId，若该doc代表文件，则did为该文件所属目录的id，若该doc代表目录，则did为该目录的上一级目录(父目录)的id|  
|**si**|Float|文件大小,若该doc代表文件，则si为该文件的大小，若该doc代表目录，则si为空|  
|**ult**|Date|upload_time，若该doc代表文件，则ult为该文件的上传时间，若该doc代表目录，则ult为该目录的创建时间|  
|**upt**|Date|update_time，若该doc代表文件，则upt为该文件的最近修改时间，若该doc代表目录，则upt为空|  
|**dlc**|Int|download_count，若该doc代表文件，则dlc为该文件的下载次数，若该doc代表目录，则dlc为空|    
|**bac**|List|backup，若该doc代表文件，则bac为该文件的备份地址，若该doc代表目录，则bac为空|  
|**arc**|List|archive，若该doc代表文件，则arc为该文件的归档地址，若该doc代表目录，则arc为空|  
|**sh**|Boolean|shared，若该doc代表文件，则sh用于判断文件是否允许共享，若sh为True，则文件可共享，若sh为False，则文件不能共享，且shp，stl，sst，set等字段为空；若该doc代表目录，则sh为空|  
|**shp**|String|share_password，若该doc代表文件，且允许共享，则shp为该文件的共享密码，若该doc代表目录，则shp为空|  
|**stl**|Boolean|share_time_limit，若该doc代表文件，且允许共享，则stl用于判断该文件是否有共享时间限制，若stl为True，则文件有共享时间限制，若stl为False，则文件无共享时间限制，且sst，set等字段为空；若该doc代表目录，则stl为空|  
|**sst**|Date|share_start_time，若该doc代表文件，允许共享且有时间限制，则sst为该文件的共享起始时间，若该doc代表目录，则sst为空|  
|**set**|Date|share_end_time，若该doc代表文件，允许共享且有时间限制，则sst为该文件的共享终止时间，若该doc代表目录，则set为空|  

### 附：
假设用户名为“user123”的用户创建了一个名为“mybucket”的bucket，则在mongodb的metadata数据库中，有collection及其中doc字段如下：

	from mongoengine import *  

	connect('metadata')  

	class user123_mybucket(DynamicDocument): 
		na = StringField(required = True)  
		fod = BooleanField(required = True)
		dir = StringField(required = True)  
		si = FloatField()  
		ult = DateTimeField()  
		upt = DateTimeField()  
		dlc = IntField()  
		bac = ListField(StringField())  
		arc = ListField(StringField())  
		sh = BooleanField()  
		shp = StringField()  
		stl = BooleanField()  
		sst = DateTimeField()  
		set = DateTimeField()  


