# coding: utf-8

import os, subprocess

def get_command_prefix(credentials, required_format="array"):
	if required_format == "array":
		if credentials['auth_method'] == "password":
			return ["sshpass", "-p", credentials['password']]
		return []
	else:
		if credentials['auth_method'] == "password":
			return "sshpass -p " + credentials['password']
		return ""

def verify_connection(credentials, command=["ls"]):
	try:
		subprocess.check_output(get_command_prefix(credentials) + ["ssh", credentials['username'] + "@" + credentials['server'], "-p", str(credentials['port'])] + command)
	except subprocess.CalledProcessError as e:
		print(e.output)
		return False
	return True

def directory_exists(credentials, path):
	return verify_connection(credentials, ["ls", path])

def make_backup(backup_name, credentials, path, tmp_dir):
	print(backup_name + ": Saving directory " + path)
	os.system(get_command_prefix(credentials, "string") + " rsync -az -e 'ssh -p " + str(credentials['port']) + "' --ignore-existing " + credentials['username'] + "@" + credentials['server'] + ":" + path + " " + tmp_dir + backup_name)
	print(backup_name + ": Directory " + path + " successfully saved")

def upload_file(credentials, target_path, backup_path):
	print("Uploading final backup file...")

	os.system(get_command_prefix(credentials, "string") + " rsync -az -e 'ssh -p " + str(credentials['port']) + "' --ignore-existing " + backup_path + " " + credentials['username'] + "@" + credentials['server'] + ":" + target_path)
	os.system("rm " + backup_path)

	print('Final backup file sucessfully uploaded')