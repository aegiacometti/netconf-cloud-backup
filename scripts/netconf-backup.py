from sys import argv, exit
from time import localtime, strftime
from glob import glob
from os import remove, path, mkdir

device_hostname = argv[1]
filename_path = argv[2]
backup_dir = argv[3]
keep_local_history = argv[4]
historic_files_to_keep = argv[5]


if not backup_dir.endswith('/'):
    backup_dir = backup_dir + '/'


def remove_old_files():
    list_files = glob(backup_dir + '{}*'.format(device_hostname))

    if len(list_files) >= int(historic_files_to_keep):
        list_files.sort(reverse=True)
        for index in range(int(historic_files_to_keep), len(list_files)):
            remove(list_files[index])


def search_changed_config_file():
    list_files = glob(backup_dir + '{}*'.format(device_hostname))

    if len(list_files) == 0:
        return True

    list_files.sort()
    last_file = open(list_files[-1], 'r')
    last_file_text = last_file.read()

    return current_config_text != last_file_text


def save_file_with_date():
    get_date = localtime()
    current_date = strftime('%Y-%m-%d-%H-%M-%S', get_date)

    filename = backup_dir + '{}.cfg.{}'.format(device_hostname, current_date)
    file = open(filename, 'w')
    file.write(current_config_text)
    file.close()


def check_dir():
    if not path.exists(backup_dir):
        try:
            mkdir(backup_dir)
        except OSError:
            print("Creation of backup directories at %s failed" % backup_dir)
            return False
        else:
            return True

    if not path.exists(backup_dir + 'github-staging'):
        try:
            mkdir(backup_dir + 'github-staging')
        except OSError:
            print("Creation of backup directories at %s failed" % (backup_dir + 'staging'))
            return False
        else:
            return True
    else:
        return True


def save_file_to_github_staging():
    filename = backup_dir + 'github-staging/{}.cfg'.format(device_hostname)

    if path.exists(filename):
        git_filename = open(filename, 'r')
        git_current_filename_text = git_filename.read()
        git_filename.close()

        if current_config_text != git_current_filename_text:
            file = open(filename, 'w')
            file.write(current_config_text)
            file.close()
    else:
        file = open(filename, 'w')
        file.write(current_config_text)
        file.close()


if __name__ == '__main__':
    read_file = open(backup_dir + filename_path, 'r')
    current_config_text = read_file.read()
    read_file.close()
    remove(backup_dir + filename_path)
    if check_dir():
        save_file_to_github_staging()
        if keep_local_history == 'yes':
            if search_changed_config_file():
                save_file_with_date()
            remove_old_files()
    else:
        exit(1)
