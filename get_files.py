import pysftp
from password_handler import get_password_handler
import logging
import sys
import getopt
import os


class UserArgs:
    def __init__(self, hostname=None, username=None, password_data=None, password_handler=None, loglevel="info",
                 remote_dir=None, local_dir=None, delete_remote=False):
        self.delete_remote = delete_remote
        self.local_dir = local_dir
        self.remote_dir = remote_dir
        self.username = username
        self.password_data = password_data
        self.hostname = hostname
        self.loglevel = loglevel
        self.password_handler = password_handler

    def __str__(self):
        return '{}(hostname={}, username={}, password_data={}, password_handler={}, loglevel={}, remote_dir={}, ' \
                'local_dir={}, delete_dir={})'.format(
                        self.__class__.__name__,
                        self.hostname,
                        self.username,
                        "**********",
                        self.password_handler,
                        self.loglevel,
                        self.remote_dir,
                        self.local_dir,
                        self.delete_remote)


def get_connection(host, username, password):
    logging.debug(f"Getting connection to host '{host}' for user '{username}'")
    opts = pysftp.CnOpts()
    opts.hostkeys = None
    connection = pysftp.Connection(host, username=username, password=password, cnopts=opts, port=2222)
    logging.debug("Got connection")
    return connection


def check_remote_dir_exists(sftp, remote_dir):
    if remote_dir is not None:
        return sftp.exists(remote_dir)


def check_local_dir_exists(local_dir=None):
    if local_dir is not None:
        return os.path.exists(local_dir)


def get_filenames(sftp, remote_dir=None):
    # with sftp:
    if remote_dir:
        sftp.chdir(remote_dir)
    files = sftp.listdir()

    if logging.DEBUG >= logging.root.level:
        num_files = len(files)
        for fl in range(0, num_files):
            logging.debug(f"Found remote file: [{fl}/{num_files}] '{files[fl]}'")

    return files


def download_files(sftp, files, remote_dir=None, local_dir=None, delete_once_downloaded=False):
    with sftp:
        if local_dir:
            os.chdir(local_dir)
        for f in files:
            sftp.get(f)
            if not os.path.isfile(os.path.join(local_dir, f)):
                logging.error(f"Failed to get file '{f}' into local_dir '{local_dir}' from remote_dir '{remote_dir}'")
            else:
                logging.info(f"Downloaded file '{f}' into local_dir '{local_dir}'")
                if delete_once_downloaded:
                    sftp.remove(f)
                    if sftp.exists(f):
                        logging.error(f"Unable to remove remote file '{f}' in remote_dir '{remote_dir}'")


def setup_logging(loglevel=None):
    if loglevel:
        level = getattr(logging, loglevel.upper(), None)
        if not isinstance(level, int):
            raise ValueError('Invalid log level: %s' % loglevel)
    else:
        level = logging.INFO
    logging.basicConfig(level=level, format='%(asctime)s %(message)s', datefmt='%Y%m%d %H:%M:%S')


def print_help(code=None):
    print('get_files.py -u <username> -p <password_data> -s <hostname> -x <password_handler> -l <log level>')
    print('get_files.py --username=<username> --password_data=<password_data> --hostname=<hostname> ',
          '--password_handler=<password_handler> --log=<log level>')
    if code:
        sys.exit(code)
    else:
        sys.exit()


def get_args(argv):
    try:
        username, hostname, password_data, password_handler, loglevel, remote_dir, local_dir, delete_remote = \
            None, None, None, None, None, None, None, False

        opts, args = getopt.getopt(argv, "hs:u:p:x:g:r:l:d:",
                                   ["log=", "username=", "password_data=", "hostname=", "password_handler=",
                                    "hostname=", "remote_dir=", "local_dir=", "--delete_remote="])
        for opt, arg in opts:
            if opt == '-h':
                print_help()
            elif opt in ['s', '--hostname']:
                hostname = arg
            elif opt in ['x', '--password_handler']:
                password_handler = arg
            elif opt in ['u', '--username']:
                username = arg
            elif opt in ['p', '--password_data']:
                password_data = arg
            elif opt in ['g', '--log']:
                loglevel = arg
            elif opt in ['r', '--remote_dir']:
                remote_dir = arg
            elif opt in ['l', '--local_dir']:
                local_dir = arg
            elif opt in ['d', '--delete_remote']:
                local_dir = arg

        user_args = UserArgs(username=username, password_data=password_data, hostname=hostname, loglevel=loglevel,
                             password_handler=password_handler, remote_dir=remote_dir, local_dir=local_dir,
                             delete_remote=delete_remote)
        logging.debug(user_args)
        return user_args
    except getopt.GetoptError as e:
        print("Error with command line options", e)
        print_help(2)


def main(argv):
    args = get_args(argv)
    setup_logging(args.loglevel)

    password = get_password_handler(args.password_handler, args.password_data)

    sftp = None
    try:
        sftp = get_connection(args.hostname, args.username, password)
        remote_exists = check_remote_dir_exists(sftp, args.remote_dir)
        if not remote_exists:
            raise Exception(f"Required remote_dir does not exist '{args.remote_dir}'")

        local_exists = check_local_dir_exists(args.local_dir)
        if not local_exists:
            try:
                logging.info(f"Local dir '{args.local_dir}' does not exist - creating it")
                os.mkdir(args.local_dir)
            except OSError as e:
                logging.error(f"Failed to create local_dir '{args.local_dir}'")
                raise e

        files = get_filenames(sftp, args.remote_dir)
        if len(files) == 0:
            logging.info("No files in remote dir - nothing to do")
            sys.exit()

        download_files(sftp, files, remote_dir=args.remote_dir, local_dir=args.local_dir,
                       delete_once_downloaded=args.delete_remote)

    except Exception as e:
        print("ERROR ", e)
    finally:
        if sftp is not None:
            sftp.close()


if __name__ == '__main__':
    main(sys.argv[1:])
