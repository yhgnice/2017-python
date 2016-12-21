#!/usr/bin/env python
# -*- coding: utf-8 -*-

from fabric.api import *
from fabric.colors import *
import os
import sys
import zipfile
import shutil
import time
from cmdcolor import *

 

env.hosts = ['IP address']
env.port = 22
env.user = 'root'
env.key_filename = r"D:\\Sessions\\key\\keyfile"


@runs_once
def target(path):
	'target packages'
	try:
		os.chdir(path)
		os.makedirs(r'aj2server\webapps')
		shutil.move('gameserverweb', r'aj2server\webapps')

		zipname = 'aj2server.zip'
		f = zipfile.ZipFile(zipname, 'w', zipfile.ZIP_DEFLATED)
		for dirpath, dirnames, filenames in os.walk('.'):
			for filename in filenames:

				if 'aj2server.zip' not in os.path.join(dirpath, filename).split('buildtmp\\')[-1]:
					f.write(os.path.join(dirpath, filename).split('buildtmp\\')[-1])
	except Exception, e:
		print e
	finally:
		f.close()


@runs_once
def delfile(path):
	# delete  dir and files
	dirs = ['gamejarclasses', 'gamepage', 'jar']
	try:
		os.chdir(path)
		for ldir in dirs:
			if os.path.exists(ldir):
				shutil.rmtree(ldir)
		if os.path.isfile(r'gameserverweb\WEB-INF\process\build-scriptlib.jar'):
			os.remove(r'gameserverweb\WEB-INF\process\build-scriptlib.jar')

		if os.path.isdir(os.path.join(path, r'gameserverweb\WEB-INF\shell')):
			shutil.rmtree(r'gameserverweb\WEB-INF\shell')
		if os.path.isdir(os.path.join(path, r'gameserverweb\gm')):
			shutil.rmtree(r'gameserverweb\gm')
		os.chdir(r'gameserverweb\WEB-INF')
		shutil.rmtree('runtimejar')
		for x in os.listdir(os.getcwd()):
			# print x
			if os.path.isfile(x):
				os.remove(x)
	except Exception, e:
		print e


@task
def deploy(path, dirput):
	with lcd(path):
		remotedir = '/data/upgrade/%s/' % dirput
		# run('mkdir %s')
		# print run('test -d {dir}').format(dir=remotedir)
		put('aj2server.zip', remotedir)
		printGreen(u'完成上传\n'.encode('gb2312'))


@task
def upgrade(version):
	# cmd='cd /root/shell;sh test.upgrade.sh  %s' % version
	cmd = 'cd /root/shell;sh one.test.upgrade.sh  %s' % version
	run(cmd)
	printGreen(u' 更新完成\n'.encode('gb2312'))


def localrelease(path):
	lcd(os.path.split(path)[0])

	os.chdir(os.path.split(path)[0])
	print os.getcwd()
	os.system('ant release')

 

@task
def go():
	localrelease(filepath)
	delfile(filepath)
	printDarkGreen(u'开始打包上传\n'.encode('gb2312'))
	target(filepath)
	deploy(filepath, dirs)
	upgrade(dirs)
	printDarkGreen(u'开始更新发布\n'.encode('gb2312'))


dirs = time.strftime("%m%d", time.localtime())
filepath = r'c:\item_builder\buildtmp'
if __name__ == '__main__':
	go()
