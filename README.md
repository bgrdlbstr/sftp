# SFTP File Grabber
Grabs files from the remote host, saves locally.

Optional delete remote file: useful to avoid dupes in future re-runs.

## Dependencies
python3 (tested on 3.8)

pip install pysftp

## Run As
get_files.py -h
get_files.py --log=DEBUG --username=foo --password_data=pass --password_handler=PlainText --hostname=localhost --remote_dir=download --local_dir=/tmp/dave-files

## Test environment
### Local sftp server
docker run -v /home/david/test-files/download:/home/foo/download -p 2222:22 -d atmoz/sftp foo:pass:1001

### Make some files locally to serve up as if they were remote
mkdir -p /home/david/test-files/download

while [[ $i -gt 0 ]]; do

head -c 512 < /dev/urandom > dave_test_$i.txt

i=$(($i-1))      

done

### Check files available in local test sftp server
sftp -P 2222 foo@localhost

(password is pass or whatever you set in the docker line above)

at the prompt use the normal sftp commands

cd download

ls *txt
 