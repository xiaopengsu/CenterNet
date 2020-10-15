import os
from string import maketrans
import sys

# file_object = open('data_1_right.txt', 'w')
# # file_object = open('rgb.csv','w')
# fileList = os.listdir("./data_1_right")
# fileList = sorted(fileList)
# for name in fileList:
# 	filename = name.replace('.', '.')
# 	filename = filename.strip('.jpg')
# 	file_object.writelines(filename + ' ' + filename + '.jpg\n')
# # file_object.writelines(filename+'.jpg\n')
# file_object.close()


def image_name_extract(file_path):
	"""extract  image name list from folder argv """
	file_object = open(file_path+'.txt','w')
	# file_object = open('rgb.csv','w')
	fileList = os.listdir('./'+file_path)
	fileList=sorted(fileList)
	for name in fileList:
		filename = name.replace('.','.')
		filename = filename.strip('.jpg')
		#file_object.writelines(filename+' '+filename+'.jpg\n')
		file_object.writelines(filename+'.jpg\n')
	file_object.close()

if __name__=="__main__":
	image_name_extract(sys.argv[1]) # data_1_right
