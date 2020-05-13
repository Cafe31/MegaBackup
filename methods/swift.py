# coding: utf-8

import swiftclient, keystoneclient

def upload_file(credentials, target_path, backup_path, backup_name):
	conn = swiftclient.Connection(
		user=credentials['tenant_name'] + ":" + credentials['username'],
		key=credentials['password'],
		authurl=credentials['auth_url'],
		auth_version=str(credentials['auth_version']),
		os_options={
			"region_name": credentials['region_name']
		}
	)

	with open(backup_path + backup_name, 'rb') as local:
		conn.put_object(
			credentials['container'],
			target_path + backup_name,
			contents=local,
			content_type='text/plain'
		)

	try:
		resp_headers = conn.head_object(credentials['container'], target_path + backup_name)
		print('The object ' + backup_name + ' was successfully uploaded in ' + credentials['container'] + target_path)
	except Exception as e:
		print('An error occurred checking for the existence of the object in container')
