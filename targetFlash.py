#!/usr/bin/env python
# -*- coding: utf-8 -*-
import codecs
import json
import multiprocessing
import os
import re
import signal
import sys

import MySQLdb
import configparser

reload(sys)
sys.setdefaultencoding('utf-8')


def get_table_value(table):
	try:
		Tvalue = []
		sql = 'desc %s' % table
		data = mysql_connect(sql)
		for line in data:
			if 'F_' in line[0]:
				Tvalue.append(line[0])
		if len(Tvalue) == 0:
			exit(0)
		return Tvalue
	except Exception, e:
		print e


def get_table_data(table, values):
	try:
		# data=[]
		sql = 'select  {values} from {table}  '.format(values=','.join(values), table=table)
		data = mysql_connect(sql)
		return data
	except Exception, e:
		print e


def mysql_connect(sql):
	try:
		database = MySQLdb.connect(host=db_host, user=db_user, port=db_port, passwd=db_pwd, db=db_name,
		                           charset='utf8')
		cursor = database.cursor()
		# result = cursor.fetchall(sql)
		cursor.execute(sql)
		result = cursor.fetchall()
		return result
		cursor.close()
		database.close()
	except Exception, e:
		print  e


def converdata(table, data):
	try:
		res = []
		dic = {}
		for line in data:
			#print data #[[(u'id', 3002L), (u'kind', 4), (u'batch_use', 0L), (u'use_type', 1L), (u'grade', 0L), (u'popsinger', 0L), (u'quickbar', 1), (u'use_desc_i18n', u'\u56de\u590d\u751f\u547d   160')
			for xline in line:
				# data = ('"%s":%s') % (xline[0], xline[1])
				dic[xline[0]] = xline[1]
			res.append(dic.copy())
			dic.clear()


		resdata = json.dumps(res, ensure_ascii=False)
		newdata = str(resdata).replace('}, {','},{').replace('": ','":').replace(', "',',"')

		write_txt(table, newdata)
	except Exception, e:
		print e


def write_txt(table, data):
	try:
		with codecs.open(os.path.join(outpath, table), 'a', 'utf-8') as fname:
			fname.write(data)
		# fname.write('\n')
	except Exception, e:
		print e


def config(cfgfile):
	try:
		cf = configparser.ConfigParser()
		cf.read(cfgfile)
		db_host = cf.get("database", "host")
		db_port = cf.getint("database", "port")
		db_user = cf.get("database", "user")
		db_pwd = cf.get("database", "password")
		db_name = cf.get("database", "name")
		db_charset = cf.get("database", "charset")
		outpath = cf.get("database", "outpath")
		return db_host, db_port, db_user, db_pwd, db_name, db_charset, outpath
	except Exception, e:
		print e


def get_tables():  # 获取数据库表
	try:
		result_tables = []
		# pattern = re.compile(r'^s_|^t_')
		pattern = re.compile(r'^v_')
		sql = 'show  tables'
		data = mysql_connect(sql)
		for line in data:
			# print line[0]
			if pattern.match(line[0]):
				pass
			# print line[0]
			else:
				# print line[0],str(line[0]).split('_',1)[1:]
				result_tables.append(line[0])

		return result_tables
	except Exception, e:
		print e


db_host, db_port, db_user, db_pwd, db_name, db_charset, outpath = config('db.conf')

'''
	if len(value_result) == 0:
		print  'no data : %s' % table
		exit(0)
'''


class GracefulExitException(Exception):
	pass


def signal_handler(signum, frame):
	raise GracefulExitException()


class GracefulExitEvent(object):
	def __init__(self, num_workers):
		self.exit_event = multiprocessing.Event()
		pass

	def is_stop(self):
		return self.exit_event.is_set()

	def notify_stop(self):
		self.exit_event.set()


def main(table):
	resultdata = []
	value_result = get_table_value(table)  # 获取表F开头字段

	new_values = [line.split('F_')[1] for line in value_result]
	# new_values = [line.split('s_')[1] for line in value_result]
	data_result = get_table_data(table=table, values=value_result)  # 获取F开头的数据

	for dataline in data_result:
		resultdata.append(zip(new_values, dataline))
	table = str(table).split('_', 1)[1:][0] + '.txt'

	if os.path.exists(os.path.join(outpath, table)):
		os.remove(os.path.join(os.path.join(outpath, table)))
	# print resultdata
	converdata(table, resultdata)  # 处理数据写入到文件


# outpath = os.path.join(os.getcwd(), 'txt')


def mian2(result_tables):
	print "main process(%d) start" % os.getpid()
	signal.signal(signal.SIGTERM, signal_handler)
	gee = GracefulExitEvent(1)
	workers = []
	for table in result_tables:
		wp = multiprocessing.Process(target=main, args=(table,))
		wp.start()
		workers.append(wp)
	try:
		for wp in workers:
			wp.join()
	except GracefulExitException:
		print "main process(%d) got GracefulExitException" % os.getpid()
		gee.notify_stop()
	for wp in workers:
		wp.join()
	print "main process(%d) exit." % os.getpid()
	sys.exit(0)


if __name__ == '__main__':
	if not os.path.exists(outpath):
		print 'Not find the path:%s' % outpath
		os._exit(0)
	result_tables = get_tables()
	# result_tables=['s_goodmodel']
	mian2(result_tables)
