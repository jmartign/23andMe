###################################################################################
# Module written to help me explore 23andMe raw data sets 
# Written by Nikhil Gopal 2-6-2011                        
# http://blog.nikhilgopal.com                              
#
# Copyright (c) 2011 Nikhil Gopal
# 
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
# 
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
# 
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
###################################################################################

import os, sys
import sqlite3

class ParseToDB:
	
	# Parses the 23andMe raw data file to a sqlite database
	def __init__(self,list_of_files):
		dbName = 'AllData.db'
		try:
			self.createDB(dbName,list_of_files)
		except sqlite3.OperationalError:
			print "Database", dbName, "already exists. Moving on..."
			return None
		for i in list_of_files:
				self.readInFilesToDB(i,dbName)
		return None
		
	# Creates a database
	def createDB(self,name,list_of_files):
		DB = sqlite3.connect(name)
		cursor = DB.cursor()
		for i in list_of_files:
			TableName = str(i.split('.')[0])
			cursor.execute('create table '+TableName+' (rsid TEXT, chr TEXT, pos TEXT, geno TEXT)')
		DB.close()
		return 0
	
	# Reads in the 23andMe raw data file into a dictionary
	def readInFilesToDB(self,infile,dbName):
		f = open(infile,'r')
		DB = sqlite3.connect(dbName)
		cursor = DB.cursor()
		for i in f.readlines():
			if '#' not in i:
				line = i.strip().split('\t')
				TableName = str(infile.split('.')[0])
				cursor.execute("insert into "+TableName+" values(?,?,?,?)", (line[0],line[1:][0],line[1:][1],line[1:][2]))
		DB.commit()
		DB.close()
		f.close()
		return 0


class ParseToDict:
	
	# Read in the raw data file into a dictionary
	def __init__(self,list_of_files):
		self.Data = {}
		for i in list_of_files:
			self.Data[i] = self.readInFile(i)
		
		# a data dictionary with a list of rsids encountered in each file
		self.RSids = self.getRSids()
		# orders files by their number of RSids
		self.FileRSidsTuple = sorted([(i,len(self.RSids[i])) for i in self.RSids], key = lambda a: -a[1])
		# max RSid
		self.MaxSize = self.FileRSidsTuple[0]
		# min RSid
		self.MinSize = self.FileRSidsTuple[-1]
		# find intersection between the input datasets
		self.Intersection = self.calcIntersectionAll()
		# a variable that contains the files provided as input
		self.files = [i for i in set(self.Data.keys())]
		return None
		
	def readInFile(self,infile):
		f = open(infile, 'r')
		rsid = {}
		for i in f.readlines():
			if '#' not in i:
				line = i.strip().split('\t')
				rsid[line[0]] = line[1:]
		f.close()
		return rsid
		
	def getRSids(self):
		self.Sizes = {}
		for i in self.Data:
			self.Sizes[i] = self.Data[i].keys()
		return self.Sizes

	def getIntersection(self,A,B):
		self.inter = set(A).intersection( set(B) )
		return self.inter
		
	def searchSNP(self,rsid):
		list = []
		for i in self.Data:
			try:
				tuple = (i, self.Data[i][rsid][-1])
				list.append(tuple)
			except:
				tuple = (i, 'N/A')
				list.append(tuple)
		return list
		
	def calcIntersectionAll(self):
		self.li = set(self.Data[self.MinSize[0]].keys())
		for i in range(len(self.files)):
			self.li = (set(self.li) & set(self.Data[self.files[i]].keys()))
		return self.li
		


if __name__ == "__main__":
	
	# Program takes 23andMe raw data files as input and they are stored in a list
	files_to_process = sys.argv[1:]
	
	# Program takes 23andMe raw data files as input and store them in a dictionary
	Datasets = ParseToDict(sys.argv[1:])