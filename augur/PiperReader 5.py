import json
import pandas as pd
#import mysql.connector
from sqlalchemy import create_engine
import sqlalchemy as s
#from sqlalchemy_utils import database_exists, create_database
from augur import logger
import os
import augur
#Count 2290
#if(line[j:j+11]=="},\"unixfrom\"" or line[j:j+9] == "},\"origin\"" ):
#9359610
#1355 aaa-dev <CAGu-7A8CzjH8ch1YdyrZid=Zq7bsVThyE5_zKGLQ0hjxDSA8ZQ@mail.gmail.com>
#<CAP3y0aZ=3eFxUbatK26H9qHV4xPJE6BdQxa=n2bqYqp45q=63A@mail.gmail.com>
#428 alto-dev
#Need to have pip install sqlalchemy-utils
def read_json(p):
		#print(p,"\n\n")
		k = j = 0
		y=""
		for line in p:
			#print(line,"\n\n")
			if(p[j:j+9] == "\"origin\":" or p[j:j+11] == "\"unixfrom\":"):
				k+=1
				#print(p[temp:j])
			y+=line
			j+=1
			if(k==2 and line == "}"):
				break
		#print(k)
		return y,j

def add_row_mess(columns1,df,di,row,archives):
	temp = 	di['data']['body']['plain']
	words = ""
	k = 1
	val = False
	#print(temp,"\n\n\nHEREEEEEEEEEEEEE!!!!!!!!!!!\n\n\n")
	prev = 0
	if(len(temp) < 100):
		j = len(temp)
	else:
		for j in range(100,len(temp),5000):
			k+=1
			li = [[di['backend_name'],di['origin'],archives,
			di['category'], di['data']['Subject'],
			di['data']['Date'], di['data']['From'],
			di['data']['Message-ID'],
			temp[prev:j] ]]
			df1 = pd.DataFrame(li,columns=columns1)
			df2 = df1.copy()
			df3 = df.append(df2)
			df = df3
			#print("prev",prev)
			#print("\n\n\n",temp[prev:j],"\n\nYEAHHHHHHHHHHHHHHHHH!!!!!!!!!!!!!!\n\n\n")
			prev = j
			row+=1
					
				#if(row==428):
					#print(df1)
				#if(row==428):
					#print("\n\n",df3,"\n\n")
	#print("jjjjjjjj",j)
	if(j+5000>len(temp)):
		k+=1
		li = [[di['backend_name'],di['origin'],archives,
		di['category'], di['data']['Subject'],
		di['data']['Date'], di['data']['From'],
		di['data']['Message-ID'],
		temp[prev:j+5000] ]]
		df1 = pd.DataFrame(li,columns=columns1)
		df2 = df1.copy()
		df3 = df.append(df2)
		df = df3
		#print("prev1",prev)
	#print(df)
	#print(len(temp),"length")
	#if(row==428):
	#	print(df3)
	#print(row)
	#if(row == 430):
	#	print(df3)
	return df,row
def add_row_mail_list(columns2,di,df_mail_list,archives):
	li = [[di['backend_name'], di['origin'], archives]]
	#print("yeah",di['origin'])
	df = pd.DataFrame(li,columns=columns2)
	#print(df)
	df4 = df_mail_list.append(df)
	return df4

class PiperMail:
	def __init__(self, user, password, host, port, dbname, ghtorrent, buildMode="auto"):
		"""
		Connect to the database

		:param dbstr: The [database string](http://docs.sqlalchemy.org/en/latest/core/engines.html) to connect to the GHTorrent database
		"""
		char = "charset=utf8"
		self.DB_STR = 'mysql+pymysql://{}:{}@{}:{}/{}?{}'.format(
		    user, password, host, port, dbname,char
		)
		#print('GHTorrentPlus: Connecting to {}:{}/{}?{} as {}'.format(host, port, dbname, char,user))
		self.db = s.create_engine(self.DB_STR, poolclass=s.pool.NullPool)
		self.ghtorrent = ghtorrent

		try:
		    	# Table creation
			if (buildMode == 'rebuild') or ((not self.db.dialect.has_table(self.db.connect(), 'issue_response_time')) and buildMode == "auto"):
				logger.info("[GHTorrentPlus] Creating Issue Response Time table...")
				self.build_issue_response_time()
		except Exception as e:
		    logger.error("Could not connect to GHTorrentPlus database. Error: " + str(e))
		#print("\nHEREEEEEEEE!!!!!!!!!\n",self.temp())
		#GHTorrentPlus.temp
		#piper.temp
		#engine = s.create_engine('mysql+mysqlconnector://root:Password@localhost/Pipermail?charset=utf8')
		#if not database_exists(engine.url):
		 #   create_database(engine.url)
		#print(os.getcwd())		
	def make(self,link):
		#print(self.db)
		print("ugh")
		print(link)
		upload  = False
		archives = ["aalldp-dev","alto-dev","advisory-group"]
		'''if("augur/notebooks" in os.getcwd()):
				os.chdir("..")
				print(os.getcwd())
				path = os.getcwd() + "/augur/" + "data/" 
		else:
			path = "data/"	'''
		print("Hey")
		path = "/augur/data/"
		db_name = "mail_lists"
		db_name_csv = os.getcwd() + path + db_name
		columns1 = 'backend_name','project','mailing_list','category','subject','date','message_from','message_id','message_text'
		df5 = pd.DataFrame(columns=columns1)
		df5.to_sql(name=db_name, con=self.db,if_exists='replace',index=False,
				dtype={'backend_name': s.types.VARCHAR(length=300),
					'project': s.types.VARCHAR(length=300),
					'mailing_list': s.types.VARCHAR(length=1000),
					'category': s.types.VARCHAR(length=300),
					'subject': s.types.VARCHAR(length=400),
					'date': s.types.VARCHAR(length=400),
					'message_from': s.types.VARCHAR(length=500),
					'message_id': s.types.VARCHAR(length=500),
					'message_text': s.types.Text				   
				})
		for i in range(len(archives)):
			place = os.getcwd() + path + 'opendaylight-' + archives[i]
			name = os.getcwd() + path + archives[i]
			#if(os.path.exists(name + '.csv')):
			#	print("File exists")
			#	continue
			f = open(place + '.json','r')
			x = f.read()
			temp = json.dumps(x)
			f.close()
			#print(y)
			data,j = read_json(x)
			#print(data,"\n\n")
			# decoding the JSON to dictionay
			di = json.loads(data)

			#print(di)
			# converting json dataset from dictionary to dataframe
			##print(di["data"]["body"]["plain"])
			#pprint.pprint(di)
			#Tried using Subject but sometimes they have fancy symbols that's
			#hard to upload to the database would have to decode it and upload
			#to the database and then encode it back when requesting from
			#the database
			columns2 = "backend_name","mailing_list_url","project"
			df = pd.DataFrame(columns=columns1)
			df5 = pd.DataFrame(columns=columns1)
			#df = df.fillna(0) # with 0s rather than NaNs
			if(i==0):
				li = [[di['backend_name'],di['origin'],archives[i]]]
				df_mail_list = pd.DataFrame(li,columns=columns2)
			#print(len(x))
			#print(j)
			row = 0
			k = 1
			y = False
			while(j<len(x)):
				df,row = add_row_mess(columns1,df,di,row,archives[i])
				df6 = df5.append(df)
				df5 = df6		
				val = False		
				#print("\n\n\n\nROWWWWWWWWWWW!!!!!!!!! ",row,"\n\n\n")
				if(row>=( (k*5000))):
					#print("\n\n\n\nHEREEEEEEEEEEEEEE!!!!!!!!!!!!\n\n\n\n")
					y+=1
					#df = df.reset_index(drop=True):
					df5.to_sql(name=db_name, con=self.db,if_exists='append',index=False)
					df5.to_csv(db_name_csv + ".csv", mode='a')
					val = True
					#print(df)
					#break
					y = True
				df = pd.DataFrame(columns=columns1)
				data,r= read_json(x[j:])
				j+=r
				#print(di,"\n\n\nSigh!!!!!!!!!!!!\n\n\n")
				#print(j,"\n\n\n")
				if(j==len(x)):
					break
				di = json.loads(data)
			if(val == False):
				#df = df.reset_index(drop=True)
				df5.to_sql(name=db_name, con=self.db,if_exists='append',index=False)
				df5.to_csv(db_name_csv + ".csv", mode='a')
			if(i!=0):
				df_mail_list = add_row_mail_list(columns2,di,df_mail_list,archives[i])
			#df = df.reset_index(drop=True)
			#df.to_csv(name + ".csv", mode='a')
			#print(archives[i])
			#df.to_sql(name=archives[i], con=self.db,if_exists='append',index=False)
			print("File uploaded ",row)
			upload = True
		print(upload)
		if(upload == True):
			#print(df_mail_list)
			#df_mail_list = df_mail_list.reset_index(drop=True)
			name = os.getcwd() + path + "Mailing_List"
			df_mail_list.to_csv(name + ".csv")
			#print("Here")
			df_mail_list.to_sql(name='mailing_list_jobs',con=self.db,if_exists='replace',index=False)
		print("Finished")
	
