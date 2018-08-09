import json
import pandas as pd
from sqlalchemy import create_engine
import sqlalchemy as s
from augur import logger
import os
import augur
import datetime
from dateutil.parser import parse
from datetime import datetime, timedelta
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import scoped_session, sessionmaker



class PiperMail:
	"""
	Takes the emails downloaded using Perceval pipermail and parsed by the jupyter
	notebook PiperMail and stores it in a pandas DataFrame format and uploads it to 
	a SQL Database
	"""
	
	def make(self,db,mail_check,archives,mail_lists,res,session,di,numb):
		"""
		First checks to see if the mail lists are in the SQL Database, if not creates a new
		table called "mail_lists" and initializes it with a set of columns ('message_text','mailing_list' etc.)
		After begins to count the number of lines in the 'mail_lists' if it's the first time will be 0, if not the column
		'augurmsgID' will be set to the number of rows+1. Then begins adding the emails to 'mail_lists' table and
		at the end adds the repositories downloaded to a table 'mailing_list_jobs' and the date of the last message
		in the mailing list.

		:param db:connection to database
		:param mail_check:dictionary of mailing list and if it is 'new' or 'update'
		:param archives:list of mailing list
		:param res:Stores all the mailing lists that is in the SQL Table 'mailing_list_jobs'
		:param session:Allows access to the SQL Tables and ability to change the table in python
		:param di: messages in mailing list
		:param numb:row number in SQL Table (would be 'augurmsgID' in SQL Table)
		"""
		

		path = "/augur/data/"
		db_name = "mail_lists"
		db_name_csv = os.getcwd() + path + db_name
		columns1 = 'augurmsgID', 'backend_name','project','mailing_list','category',\
		           'message_part','message_parts_tot', 'subject','date',\
				   'message_from','message_id','message_text'
		df5 = pd.DataFrame(columns=columns1)
		columns2 = "augurlistID" ,"backend_name","mailing_list_url","project","last_message_date"
		df_mail_list = pd.DataFrame(columns=columns2)
		if(not mail_lists):			
			df5.to_sql(name=db_name, con=db,if_exists='replace',index=False,
					dtype={'augurmsgID': s.types.Integer,
						'backend_name': s.types.VARCHAR(length=300),
						'project': s.types.VARCHAR(length=300),
						'mailing_list': s.types.VARCHAR(length=1000),
						'category': s.types.VARCHAR(length=300),
						'message_part': s.types.Integer,
						'message_parts_tot': s.types.Integer,
						'subject': s.types.VARCHAR(length=400),
						'date': s.types.DateTime(),
						'message_from': s.types.VARCHAR(length=500),
						'message_id': s.types.VARCHAR(length=500),
						'message_text': s.types.VARCHAR(length=12000)
					})
			mail_lists = True
		
		#print(di[0]['data']['Date'])	
		SQL = s.sql.text("""SELECT COUNT(*) FROM mail_lists""")
		df7 = pd.read_sql(SQL, db)
		augurmsgID = int(df7.values)+1
		for i in range(len(archives)):
			if(mail_check[archives[i]] == "update"):
				new = False
			elif(mail_check[archives[i]] == 'new' ):
				#place = os.getcwd() + path + 'archive-' + archives[i]
				new = True
			else:
				print("Skipping")
				continue
			print(archives)
			df = pd.DataFrame(columns=columns1)
			df["date"] = pd.to_datetime(df["date"])
			df5 = pd.DataFrame(columns=columns1)
			#columns2= "backend_name","mailing_list_url","project"
			last_date = self.convert_date(di[0]['data']['Date'])
			row = 1
			k = 1
			y = False
			for j in range(len(di)):
				df,row,augurmsgID = self.add_row_mess(columns1,df,di[j],row,archives[0],augurmsgID)
				df6 = df5.append(df)
				df5 = df6		
				val = False		
				if(row>=( (k*5000))):
					y+=1
					df5.to_sql(name=db_name, con=db,if_exists='append',index=False)
					val = True
					y = True
				df = pd.DataFrame(columns=columns1)
			if(val == False):
				df5.to_sql(name=db_name, con=db,if_exists='append',index=False)
			temp_date = self.convert_date(di[j]['data']['Date'])
			if(last_date < temp_date):
				last_date = temp_date
				print(last_date)
				if(mail_check[archives[0]] == 'update'):
					print(res)
					print("sigh")
					y=0
					print(res[y].project)
					while(res[y].project!=archives[0]):
						y+=1
						print(res[y].project)
					res[y].last_message_date = last_date
					session.commit()

			df_mail_list,numb = self.add_row_mail_list(columns2,di[i],df_mail_list,archives[0],last_date,numb)
			print("File uploaded ",row)
		if(new == True):
			name = os.getcwd() + path + "mailing_list_jobs"
			df_mail_list.to_sql(name='mailing_list_jobs',con=db,if_exists='append',index=False)
			print("Mailing List Job uploaded")
		print("Finished")
		return numb,mail_lists
	
	def convert_date(self,di):
		'''
		Converts the date of the message in the email to a datetime object
		to be uploaded to the SQL Database 'mail_lists'

		param di: messages in mailing list
		'''
		split = di.split()
		sign = split[5][0]
		if sign == '-':
			sign = +1
		else:
			sign = -1
		hours = int(split[5][1:3]) * sign
		mins = int(split[5][3:6]) * sign
		s = " "
		date = parse(s.join(split[:5]))
		date = date + timedelta(hours = hours)
		date = date + timedelta(minutes = mins)
		return date

	def add_row_mess(self,columns1,df,di,row,archives,augurmsgID):

		'''
		Converts the messages in the mailing list to a format that could be uploaded
		to the SQL Table 'mail_lists'. If the message is too long, it divides it into 
		seperate parts that will be uploaded to the 'mail_lists'

		param columns1: All the columns in the SQL Table 'mail_lists' (e.g. 'augurmsgID', 'message_id')
		param df: Dataframe that holds the messages which is uploaded to 'mail_lists'
		param di: Dictionary that holds the messages that will then be transfered to df
		param row: The number of rows needed for the message (it would be more than 1 
		           if the message is split into multiple parts)
		param archives: List of mailing list
		param augurmsgID: The current row number in 'mail_lists'
		'''
		temp = 	di['data']['body']['plain']
		k = 1
		val = False
		prev = 0
		length = len(temp)
		#print(length)
		mess_row_tot = 1
		row_num = 0
		if(length < 100):
			j = length
		else:
			mess_row_tot+= int(length/7000)
			if( (mess_row_tot*7000) > length ):
				mess_row_tot+=1
			for j in range(100,length,7000):
				row_num+=1
				k+=1
				date = self.convert_date(di['data']['Date'])
				li = [[augurmsgID,di['backend_name'],di['origin'],archives,
				di['category'], row_num, mess_row_tot, di['data']['Subject'],
				date, di['data']['From'],
				di['data']['Message-ID'],
				temp[prev:j] ]]
				df1 = pd.DataFrame(li,columns=columns1)
				df3 = df.append(df1)
				df = df3
				prev = j
				row+=1
				augurmsgID+=1
		if(j+7000>length):
			k+=1
			row_num+=1
			li = [[augurmsgID,di['backend_name'],di['origin'],archives,
			di['category'], row_num, mess_row_tot, di['data']['Subject'],
			date, di['data']['From'],
			di['data']['Message-ID'],
			temp[prev:j+7000] ]]
			df1 = pd.DataFrame(li,columns=columns1)
			df3 = df.append(df1)
			df = df3
			augurmsgID+=1
		row+=row_num
		return df,row,augurmsgID
	
	def add_row_mail_list(self,columns2,di,df_mail_list,archives,last_date,numb):
		'''
		Converts the details about the current mailing list in a format that could
		be uploaded to the SQL Table 'mailing_list_jobs'. 

		param columns2: All the columns in the SQL Table 'mailing_list_jobs'
		                (e.g. 'augurlistID', 'mailing_list_url')
		param di: Dictionary that holds the messages that will then be transfered to df_mail_list
		param df_mail_list: Dataframe that holds the information which is uploaded to 'mailing_list_jobs'		
		param archives: List of mailing list
		param numb: The current row number in 'mailing_list_jobs'
		param numb: The current row number in 'mailing_list_jobs'

		'''
		li = [[numb,di['backend_name'], di['origin'], archives,last_date]]
		df = pd.DataFrame(li,columns=columns2)
		df4 = df_mail_list.append(df)
		df_mail_list = df4
		numb+=1
		return df_mail_list,numb
	
