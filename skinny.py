# Skinny class handler
import wcommon as wc
import os

class SKINNY():
	def __init__(self, skinnyIP):
		self.skinnyIP = skinnyIP
		self.getsqc_url = 'http://%s:31416/getsqc/' % self.skinnyIP
		self.__name__ = 'SKINNY'
	def GetSQC(self, modemIP):
		data = wc.REST_GET(self.getsqc_url + modemIP)
		return(data)

