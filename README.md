# MegaBackup
MegaBackup is a python backup tool to save distant database or directory into AWS S3, Openstack Swift or an SSH source.

You only have to specify login credentials for sources and target in config.json file

<h1>Installation</h1>

You need python3 to use this tool. I tested it on Debian/Ubuntu.

Then, you only have to follow these steps:
<pre>
apt-get install sshpass rsync mariadb-client git
git clone https://github.com/Cafe31/MegaBackup.git
</pre>

If you want to upload your backup on S3 or Openstack Swift, you need to install the following modules:

S3:<pre>pip install boto3</pre>
Swift:<pre>pip install python-swiftclient python-keystoneclient</pre>

<h1>Configuration</h1>

You only have to edit config.json file with your login credentials:

| Variable     | Description                                                  |
| ------------ | ------------------------------------------------------------ |
| tmp_dir    | Path of temporary directory (must end with a slash)   |
| date_format   | "timestamp" (1588258810) or "date" (2020-04-30) used to rename your backup file backup-date_format.tar.gz. You should use timestamp if you make a backup more frequently than daily |
| compression_algorith | Only "gzip" is supported for the moment   |
| type  | database/files for sources, and s3/swift/files for target |
| sources | You can set several sources, separated by commas |
| path | Path for the target (must end with a slash) |
| auth_method | Can be set on "ssh_key" or "password" |

For each connection type, credential informations needed are detailed in examples.txt

<h1>Restore a backup</h1>

You can restore data from a backup file as below:
<pre>python3 main.py restore backup_file_name.tar.gz backup_name_to_restore other_backup_name_to_restore</pre>

Note: MegaBackup will download the specified backup file from the target speficied in config.json

In the case you want to restore a backup on a new server, you need to change server_address credentials for specified backup

<h1>Make a daily backup</h1>

You can add a crontab to make a new backup everyday:
<pre>0 3 * * * python3 /path/main.py backup</pre>
