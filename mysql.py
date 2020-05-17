# coding: utf-8

import os, subprocess

#check if a databse is available with entered credentials
def verify_connection(credentials, database):
	if credentials['auth_method'] == "ssh_key":
		return False

	try:
		subprocess.check_output(["mysql", "-h", credentials['server'],  "-P", str(credentials['port']), "-u", credentials['username'], "-p" + credentials['password'], "-e", "exit", database])
	except subprocess.CalledProcessError as e:
		print(e.output)
		return False
	return True

#save a database into a file
def make_backup(backup_name, credentials, database, tmp_dir):
	os.system("mysqldump -h " + credentials['server'] + " -P " + str(credentials['port']) + " -u " + credentials['username'] + " -p" + credentials['password'] + " " + database + " > " + tmp_dir + backup_name + "/" + database + ".sql")
	print(backup_name + ": Database " + database + " successfully saved")

#restore a database using .sql file
def restore_backup(backup_name, credentials, database, tmp_dir):
	os.system("mysql -h " + credentials['server'] + " -P " + str(credentials['port']) + " -u " + credentials['username'] + " -p" + credentials['password'] + " " + database + " < " + tmp_dir + backup_name + "/" + database + ".sql")
	print(backup_name + ": Database " + database + " successfully restored")

#create a new database on a MySQL server
def create_database(backup_name, credentials, database):
	os.system("mysqladmin -h " + credentials['server'] + " -P " + str(credentials['port']) + " -u " + credentials['username'] + " -p" + credentials['password'] + " create " + database)
	
	if verify_connection(credentials, database):
		return True
	return False
