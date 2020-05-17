# coding: utf-8

#le script 

import json, os, sys, subprocess

import methods.mysql as mysql
import methods.files as files
import methods.s3 as s3
import methods.swift as swift

from functions import *

#Vérification de la présence des packets nécessaires
packets_required=["sshpass", "rsync", "mariadb-client"]
supported_compression_algorithm=["gzip"]

for packet in packets_required:
	is_packet_installed(packet)

#Lecture du fichier de configuration config.json
absolute_path=os.path.dirname(os.path.abspath(__file__))

with open(absolute_path + '/config.json') as json_file:
	try:
		data = json.load(json_file)
	except ValueError:
		exit("Incorrect json file, please check it on: https://jsonlint.com/")

tmp_dir = data['tmp_dir']

#On vide le répertoire temporaire
empty_tmp_dir(tmp_dir)

#Vérifie que l'algorithme de compression est supporté
if data['compression_algorithm'] not in supported_compression_algorithm:
	exit("The following compression algorithm is not supported : " + data['compression_algorithm'])

#Lecture des arguments et choix d'une action en fonction
if sys.argv[1] == "restore":
	#Initialisation des variables nécessaires à la restauration d'une backup
	target_credentials = data['to']['credentials']
	target_path = data['to']['path']
	global_backup_name = sys.argv[2]
	backup_path=tmp_dir

	#On récupère le dernier fichier de backup sur la source définie (files/swift/s3)
	if data['to']['type'] == "files":
		if files.directory_exists(credentials, target_path):
			files.download_file(target_credentials, target_path, backup_path + global_backup_name)
		else:
			exit("Directory " + target_path + " unreachable on " + target_credentials['server'])
	elif data['to']['type'] == "swift":
		is_module_installed("swiftclient")
		is_module_installed("keystoneclient")
		swift.download_file(target_credentials, target_path, backup_path, global_backup_name)
	elif data['to']['type'] == "s3":
		is_module_installed("boto3")
		s3.download_from_aws(target_credentials, target_path, backup_path, global_backup_name)

	#On décompresse l'archive principale contenant l'ensemble des sauvegardes
	decompress_file(tmp_dir, global_backup_name)

	#On restore chacune des sauvegardes passées en argument
	i=2
	while i < len(sys.argv)-1:
		i += 1
		backup_name = sys.argv[i]
		backup_type, credentials, sources = get_backup_infos(data['from'], backup_name) #Récupération des informations de la source

		decompress_file(tmp_dir, backup_name + ".tar.gz") #Décompression de la backup à restaurer

		if backup_type == "mysql":
			for database in sources:
				if not mysql.verify_connection(credentials, database):
					print(backup_name + ": Database " + database + "do not exist. Trying to create it...")
					if not mysql.create_database(backup_name, credentials, database):
						exit(backup_name + ": Unable to create database " + database)
				mysql.restore_backup(backup_name, credentials, database, tmp_dir)
		elif backup_type == "files":
			for path in sources:
				if files.directory_exists(credentials, path):
					files.restore_backup(backup_name, credentials, path, tmp_dir)
				else:
					exit(backup_name + ": Unable to access " + path)
		else:
			exit(backup['name'] + ": Incorrect backup type")

else:
	#On lance la sauvegarde de l'ensembles des sources indiquées dans config.json
	backup_names=[]

	for backup in data['from']:
		credentials = backup['credentials']
		backup_names.append(backup['name'])

		#Création du répertoire portant le nom backup['name'] dans le répertoire temporaire
		create_directory(tmp_dir + backup['name'])

		#Sauvegarde de la base de donnée/répertoire suivant le choix de l'utilisateur
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

		#Compression du répertoire en format .tar.gz
		compress_directory(tmp_dir, data['compression_algorithm'], backup['name'])

	#On compresse l'ensemble des archives compressées en une seule archive
	backup_path, backup_name=final_compression(tmp_dir, data['compression_algorithm'], data['date_format'], backup_names)

	#Maintenant le fichier compressé créé, on l'envoie vers la cible définir dans config.json
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
