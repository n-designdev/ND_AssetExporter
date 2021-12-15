# -*- coding: utf-8 -*-

import json
import re
import codecs

#-------------------------------------
# save
#★フォルダの有無はこれより前にチェックして下さい
#-------------------------------------
def _saveJson(path, object=None):
	if object is None:
		object = {}
	CRLF = re.compile('\r\n|\n|\r')
	try:
		jsonStr = json.dumps(object,
			ensure_ascii = False, encoding = 'utf8',
			indent = 2, sort_keys = True,
		)
		with codecs.open(path, 'w', 'utf8') as f:
			f.write(CRLF.sub('\r\n', jsonStr) + '\r\n')
		return (True)
	except:
		return (False)

#-------------------------------------
# load
#★ファイルの有無はこれより前にチェックして下さい
#-------------------------------------
def _loadJson(path):
	object = {}
	try:
		with codecs.open(path, 'r', 'utf8') as f:
			object = json.load(f)
	except:
		import traceback
		print(traceback.format_exc())

	return (object)

#-------------------------------------
# サンプル
#-------------------------------------
if __name__ == '__main__':
	filePath = 'C:/temp/test.json'

	sampleDict = {
		'file1': {'source_path': 'D:/Temp/test.jpg', 'target_path': 'D:/Temp/publish/texture/test.jpg', 'is_seq': False},
		'file2': {'source_path': 'D:/Temp/test2.1001.jpg', 'target_path': 'D:/Temp/publish/texture/test2/test2.1001.jpg', 'is_seq': True},
	}
	print ('sampleDict')
	print (sampleDict)

	#保存
	print (_saveJson(filePath, sampleDict))

	#読み込み
	object = _loadJson(filePath)
	print ('object')
	print (object)
