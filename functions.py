# coding: utf-8

import os, subprocess, time, datetime, importlib.util

#make a directory if necessary
def create_directory(path):
	os.system("mkdir -p " + path)

#check if the packet in parameter is installed on the system
def is_packet_installed(packet_name):
	try:
		subprocess.check_output(["dpkg", "-l", packet_name])
	except subprocess.CalledProcessError as e:
		exit(packet_name + " package is needed to continue")

#check if a python module is installed
def is_module_installed(module_name):
	spec = importlib.util.find_spec(module_name)
	if spec is None:
	    exit(module_name + " module is needed to continue, you should try: pip install " + module_name)

#make a .tar.gz archive and delete the old folder
def compress_directory(path, algorithm, backup_name):
	print(backup_name + ": Compressing backup ")

	os.system("tar -P -czf " + path + backup_name + ".tar.gz " + path + backup_name + " > /dev/null")
	os.system("rm -r " + path + backup_name)

	return backup_name

#delete all files in tmp_dir
def empty_tmp_dir(tmp_dir):
	os.system("rm -r " + tmp_dir + "*")

#find right credentials for backup_name in json string and return them
def get_backup_infos(json_data, backup_name):
	for backup in json_data:
		if backup['name'] == backup_name:
			return backup['type'], backup['credentials'], backup['sources']

	exit("None connection informations found for " + backup_name)


#compress all compressed backups in one
def final_compression(path, algorithm, date_format, backup_names):
	if date_format == "timestamp":
		final_name = "backup_" + str(int(time.time())) + ".tar.gz"
	elif date_format == "date":
		final_name = "backup_" + str(datetime.date.today()) + ".tar.gz"

	os.system("tar -P -czf " + path + final_name + " " + path + "*.gz > /dev/null")

	for backup_name in backup_names:
		os.system("rm " + path + backup_name + ".tar.gz")

	return path, final_name

#decompress a .tar.gz file
def decompress_file(path, filename):
	print(filename + ": Deflating compressed backup...")

	os.system("tar -P -xzf " + path + filename + " > /dev/null")

	print(filename + ": Compressed backup deflated")