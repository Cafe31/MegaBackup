# coding: utf-8

import os, subprocess, time, datetime, importlib.util

def create_directory(path):
	os.system("mkdir -p " + path)

def is_packet_installed(packet_name):
	try:
		subprocess.check_output(["dpkg", "-l", packet_name])
	except subprocess.CalledProcessError as e:
		exit(packet_name + " package is needed to continue")

def is_module_installed(module_name):
	spec = importlib.util.find_spec(module_name)
	if spec is None:
	    exit(module_name + " module is needed to continue, you should try: pip install " + module_name)

def compress_directory(path, algorithm, backup_name):
	print(backup_name + ": Compressing backup ")

	os.system("tar -P -czf " + path + backup_name + ".tar.gz " + path + backup_name + " > /dev/null")
	os.system("rm -r " + path + backup_name)

	return backup_name

def empty_tmp_dir(tmp_dir):
	os.system("rm -r " + tmp_dir + "*")

def final_compression(path, algorithm, date_format, backup_names):
	if date_format == "timestamp":
		final_name = "backup_" + str(int(time.time())) + ".tar.gz"
	elif date_format == "date":
		final_name = "backup_" + str(datetime.date.today()) + ".tar.gz"

	os.system("tar -P -czf " + path + final_name + " " + path + "*.gz > /dev/null")

	for backup_name in backup_names:
		os.system("rm " + path + backup_name + ".tar.gz")

	return path, final_name

is_module_installed("swiftclient")