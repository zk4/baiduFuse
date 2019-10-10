GET: file?method=list&path=
参数只能一个 path 
返回:
``` json
{
	"list": [{
		"app_id": 250528,
		"block_list": ["de48ad710a236553ac14b02af64e45a9"],
		"category": 1,
		"ctime": 1529324211,
		"fs_id": 573077409169150,
		"isdir": 0,
		"local_ctime": 1529271761,
		"local_mtime": 1529271847,
		"md5": "de48ad710a236553ac14b02af64e45a9",
		"mtime": 1566961298,
		"oper_id": 0,
		"path": "/netty-闪电侠/Java读源码之Netty深入剖析  [Dmz社区 DmzSheQu.Com]/10-1 性能优化工具类概述.mp4",
		"s3_handle": "",
		"server_ctime": 1529324211,
		"server_filename": "10-1 性能优化工具类概述.mp4",
		"server_mtime": 1566961298,
		"share": 0,
		"size": 2626959,
		"status": 0,
		"unlist": 0,
		"user_id": 69036212
	}
  ]
```


POST: file?method=meta
args: multiparts, support multipal paths
in  : 
``` json
{"list":[{"path": "/mobile/ps/yj/111228A006.jpg"}, {"path": "/mobile/ps/yj/111228A015.jpg"}, {"path": "/mobile/ps/yj/111228A017.jpg"}, {"path": "/mobile/ps/yj/200522A005.jpg"}, {"path": "/mobile/ps/yj/Untitled-1.psd"}, {"path": "/mobile/ps/yj/Untitled-1\u526f\u672c.jpg"}, {"path": "/mobile/ps/yj/yj.rar"}]}
```

out :
``` json
{
	"list": [{
		"app_id": 250528,
		"block_list": ["456a9a201071a748aa32f3b45813f327"],
		"category": 3,
		"ctime": 1430985589,
		"extent_int3": 0,
		"extent_tinyint1": 0,
		"extent_tinyint2": 0,
		"extent_tinyint3": 0,
		"extent_tinyint4": 0,
		"file_key": "E-pSvFuI3jvfHKI3AxjdTI5ft58zI5eLrgmI1gbJy8I1ahJ",
		"fs_id": 608783245830349,
		"isdelete": 0,
		"isdir": 0,
		"local_ctime": 1430985589,
		"local_mtime": 1430985589,
		"md5": "456a9a201071a748aa32f3b45813f327",
		"mtime": 1453044247,
		"oper_id": 0,
		"parent_path": "/mobile/ps/yj",
		"path": "/mobile/ps/yj/111228A006.jpg",
		"s3_handle": "http://bj.newbcs.bae.baidu.com/p3-1400456a9a201071a748aa32f3b45813f327d6063adc00000003dc88/456a9a201071a748aa32f3b45813f327?sign=MBOT:gNQ17x3aoMs8:1suQp%2BIiUVi0f9ai67Ip3zsDtnk%3D&time=1570886259&response-content-disposition=attachment;%20filename=111228A006.jpg&url_from_pcsui=1",
		"server_ctime": 1430985589,
		"server_filename": "111228A006.jpg",
		"server_mtime": 1453044247,
		"share": 0,
		"size": 253064,
		"status": 0,
		"user_id": 69036212
	}]
}
```
