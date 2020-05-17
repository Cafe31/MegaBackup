# coding: utf-8

import os, subprocess

#add sshpass prefix if a password is filled
def get_command_prefix(credentials, required_format="array"):
	if required_format == "array":
		if credentials['auth_method'] == "password":
			return ["sshpass", "-p", credentials['password']]
		return []
	else:
		if credentials['auth_method'] == "password":
			return "sshpass -p " + credentials['password']
		return ""

#check if a SSH server is available
def verify_connection(credentials, command=["ls"]):
	try:
		subprocess.check_output(get_command_prefix(credentials) + ["ssh", credentials['username'] + "@" + credentials['server'], "-p", str(credentials['port'])] + command)
	except subprocess.CalledProcessError as e:
		print(e.output)
		return False
	return True

#check if a path exists on an SSH server
def directory_exists(credentials, path):
	return verify_connection(credentials, ["ls", path])

#compress a directory into a .tar.gz file
def make_backup(backup_name, credentials, path, tmp_dir):
	print(backup_name + ": Saving directory " + path)
	os.system(get_command_prefix(credentials, "string") + " rsync -az -e 'ssh -p " + str(credentials['port']) + "' --ignore-existing " + credentials['username'] + "@" + credentials['server'] + ":" + path + " " + tmp_dir + backup_name)
	print(backup_name + ": Directory " + path + " successfully saved")

#upload a file using rsync
def upload_file(credentials, target_path, backup_path):
	print("Uploading final backup file...")

	os.system(get_command_prefix(credentials, "string") + " rsync -az -e 'ssh -p " + str(credentials['port']) + "' --ignore-existing " + backup_path + " " + credentials['username'] + "@" + credentials['server'] + ":" + target_path)
	os.system("rm " + backup_path)

	print('Final backup file sucessfully uploaded')

#download a file/directory from SSH source
def download_file(credentials, target_path, backup_path):
	print("Downloading backup file...")

	os.system("rm " + backup_path)
	os.system(get_command_prefix(credentials, "string") + " rsync -az -e 'ssh -p " + str(credentials['port']) + "' --ignore-existing " + credentials['username'] + "@" + credentials['server'] + ":" + target_path + " " + backup_path)

	print('Last backup file downloaded')

#upload a file/directory to an SSH source
def restore_backup(backup_name, credentials, path, tmp_dir):
	print(backup_name + ": Restoring " + path + " from backup...")

	path_splited = path.split("/")
	os.system(get_command_prefix(credentials, "string") + " rsync -az -e 'ssh -p " + str(credentials['port']) + "' " + tmp_dir + backup_name + "/" + path_splited[len(path_splited)-1] + "/ " + credentials['username'] + "@" + credentials['server'] + ":" + path)

	print(backup_name + ": Files successfully restored from backup")

