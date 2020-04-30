# coding: utf-8

import os, subprocess

def verify_connection(credentials, database):
	if credentials['auth_method'] == "ssh_key":
		return False

	try:
		subprocess.check_output(["mysql", "-h", credentials['server'],  "-P", str(credentials['port']), "-u", credentials['username'], "-p" + credentials['password'], "-e", "exit", database])
	except subprocess.CalledProcessError as e:
		print(e.output)
		return False
	return True

def make_backup(backup_name, credentials, database, tmp_dir):
	os.system("mysqldump -h " + credentials['server'] + " -P " + str(credentials['port']) + " -u " + credentials['username'] + " -p" + credentials['password'] + " " + database + " > " + tmp_dir + backup_name + "/" + database + ".sql")
	print(backup_name + ": Database " + database + " successfully saved")
