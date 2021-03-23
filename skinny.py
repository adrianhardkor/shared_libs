# Skinny class handler
import wcommon as wc
import os
import json

class SKINNY():
	def __init__(self, skinnyIP):
		self.skinnyIP = skinnyIP
		self.getsqc_url = 'http://%s:31416/getsqc/' % self.skinnyIP
		self.__name__ = 'SKINNY'
	def GetSQC(self, modemIP):
		try:
			data = json.loads(wc.REST_GET(self.getsqc_url + modemIP))
		except Exception as err:
			data = {'err':err}
		return(data)

