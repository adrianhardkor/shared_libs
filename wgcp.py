# Google Public Cloud
import wcommon as wc
import string
import pickle
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request


class GCP():
	def __init__(self, SAMPLE_SPREADSHEET_ID, SAMPLE_RANGE_NAME, SCOPES, PICKLE_TOKEN_FILE,creds_json='credentials.json'):
		self.creds_json = creds_json
		self.SAMPLE_SPREADSHEET_ID = SAMPLE_SPREADSHEET_ID
		self.SAMPLE_RANGE_NAME = SAMPLE_RANGE_NAME
		self.SCOPES = SCOPES
		self.PICKLE_TOKEN_FILE = PICKLE_TOKEN_FILE
		self.__name__ = 'GCP'

	def Connect(self):
		connect = wc.timer_index_start()
		creds = None
		if os.path.exists(self.PICKLE_TOKEN_FILE):
			with open(self.PICKLE_TOKEN_FILE, 'rb') as token:
				creds = pickle.load(token)
		if not creds or not creds.valid:
			if creds and creds.expired and creds.refresh_token:
				creds.refresh(Request())
			else:
				flow = InstalledAppFlow.from_client_secrets_file(self.creds_json, self.SCOPES)
				creds = flow.run_local_server(port=0)
			# Save the credentials for the next run
			with open(self.PICKLE_TOKEN_FILE, 'wb') as token:
				pickle.dump(creds, token)

		service = build('sheets', 'v4', credentials=creds)
		# wc.pairprint('GCP:  Connect', str(wc.timer_index_since(connect)) + ' ms')
		# Call the Sheets API
		return(service.spreadsheets().values())

	def GET(self,handle):
		getTime = wc.timer_index_start()
		out = []
		result = handle.get(spreadsheetId=self.SAMPLE_SPREADSHEET_ID, range=self.SAMPLE_RANGE_NAME).execute()
		got = result.get('values',[])
		# wc.pairprint('GCP:  GET', str(wc.timer_index_since(getTime)) + ' ms')
		return(got)

	def SET(self,handle,cell,value):
		strs,ints = wc.str_int_split(cell)
		# Check current value
		old = 'didnt_find'
		for id2 in self.got.keys():
			if self.got[id2]['Row'] == str(ints):
				for v in self.got[d2].keys():
					if str(self.got[id2][v]) == str(value): return(); # no update / already exists
		setTime = wc.timer_index_start()
		body = {'values':[[value]]}
		rangeName = self.SAMPLE_RANGE_NAME + '!' + cell
		try:
			result = handle.update(spreadsheetId=self.SAMPLE_SPREADSHEET_ID,
				range=rangeName, valueInputOption='RAW', body=body).execute()
			wc.pairprint(cell,value)
		except Exception as err:
			print('\n\n' + str(err))
		# wc.pairprint('GCP:  SET', str(wc.timer_index_since(setTime)) + ' ms')
		return()

	def CONVERT_JSON_BY_HEADER(self,sheet,headIndex):
		self.headers = sheet.pop(0)
		asset = {}
		r = 2; # 2=because there's no 0 and 1 is headers.pop(0)
		if headIndex == '': ipIndex = r
		else: ipIndex = self.headers.index(headIndex)
		for row in sheet:
			# wc.pairprint(row,ipIndex)
			if len(row)-1 < ipIndex:
				continue
			ip = row[ipIndex]
			asset[ip] = {'Row':r}
			i = 0
			for colum in row:
				# wc.pairprint('\t' + self.headers[i],colum)
				if wc.lindex_exists(self.headers, i):
					asset[ip][self.headers[i]] = colum
				else:
					# no header for colum = __D__
					asset[ip]['__' + list(string.ascii_uppercase)[i] + '__'] = colum
				i += 1
			r += 1
		self.got = asset
		return(asset)


