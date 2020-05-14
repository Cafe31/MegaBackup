# coding: utf-8

#the script must be started from his directory

import json, os, sys, subprocess

import methods.mysql as mysql
import methods.files as files
import methods.s3 as s3
import methods.swift as swift

from functions import *

#Check if the prerequisites are present
packets_required=["sshpass", "rsync", "mariadb-client"]
supported_compression_algorithm=["gzip"]

for packet in packets_required:
	is_packet_installed(packet)

with open('config.json') as json_file:
	try:
		data = json.load(json_file)
	except ValueError:
		exit("Incorrect json file, please check it on: https://jsonlint.com/")

tmp_dir = data['tmp_dir']
backup_names=[]

empty_tmp_dir(tmp_dir)

if data['compression_algorithm'] not in supported_compression_algorithm:
	exit("The following compression algorithm is not supported : " + data['compression_algorithm'])

#Downloading data from all sources
for backup in data['from']:
	credentials = backup['credentials']
	backup_names.append(backup['name'])

	create_directory(tmp_dir + backup['name'])

	if backup['type'] == "mysql":
		for database in backup['sources']:
			if mysql.verify_connection(credentials, database):
				mysql.make_backup(backup['name'], credentials, database, tmp_dir)
			else:
				exit(backup['name'] + ": Unable to access database " + database)

	elif backup['type'] == "files":
		if files.verify_connection(credentials):
			for path in backup['sources']:
				if files.directory_exists(credentials, path):
					files.make_backup(backup['name'], credentials, path, tmp_dir)
				else:
					exit(backup['name'] + ": Unable to access " + path)
		else:
			exit(backup['name'] + ": Unable to enable SSH connection to " + credentials['server'])
	else:
		exit(backup['name'] + ": Incorrect backup type")

	compress_directory(tmp_dir, data['compression_algorithm'], backup['name'])

backup_path, backup_name=final_compression(tmp_dir, data['compression_algorithm'], data['date_format'], backup_names)

#Sending the backup file to the choosed source (s3, swift, SSH)
target_credentials = data['to']['credentials']
target_path = data['to']['path']

if data['to']['type'] == "files":
	if files.directory_exists(credentials, target_path):
		files.upload_file(target_credentials, target_path, backup_path + backup_name)
	else:
		exit("Directory " + target_path + " unreachable on " + target_credentials['server'])
elif data['to']['type'] == "swift":
	is_module_installed("swiftclient")
	is_module_installed("keystoneclient")
	swift.upload_file(target_credentials, target_path, backup_path, backup_name)
elif data['to']['type'] == "s3":
	is_module_installed("boto3")
	s3.upload_to_aws(target_credentials, target_path, backup_path, backup_name)
