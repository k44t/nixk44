import os, stat, os.path
import shutil
import re
import time
import subprocess
import json
from natsort import natsorted
from datetime import datetime, timedelta
from getpass import getpass
import traceback

import argparse
import logging
import sys


# Configure the root logger
logging.basicConfig(
  level=logging.INFO,
  format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
  handlers=[
    # logging.FileHandler(logfile_path + datetime.now().strftime("%d-%m-%Y_%H:%M:%S.%f") ),  # File handler
    logging.StreamHandler(sys.stdout)   # Stream handler for stdout
  ]
)

log = logging.getLogger("vmm")

log.original_error = log.error
log.original_info = log.info
log.original_debug = log.debug
log.original_warning = log.warning
log.original_critical = log.critical
def customized_logger(level, message, *args, **kwargs):
  printCallstack = True
  if printCallstack:
    callstack = ""
    raw_tb = traceback.extract_stack()
    entries = traceback.format_list(raw_tb)
    for line in entries:
        if ".vscode-server" in line or "/nix/store/" in line or "Apoeschllogging.py" in line\
          or "customized" in line:
            continue
        else:
            regexp_pattern = r'line (.*?),'
            line_number = re.search(regexp_pattern, line).group(1)
            #line_number = clicolors.DEBUG + line_number + clicolors.OKBLUE
            regexp_pattern = r'File "(.*?)"'
            file = re.search(regexp_pattern, line).group(1)
            regexp_pattern = r'in (.*?)\n'
            function = re.search(regexp_pattern, line).group(1)
            if function == "<module>":
                callstack = callstack + file + ":" + line_number + ":" + function
            else:
                callstack = callstack + "->" + file + ":" + line_number + ":" + function
    modified_message = message + '\033[90m' + "     <<<<<<<<< " + callstack + '\033[0m'
  else:
    modified_message = message
  if level == logging.ERROR:
      log.original_error(modified_message)
  elif level == logging.INFO:
      log.original_info(modified_message)
  elif level == logging.DEBUG:
      log.original_debug(modified_message)
  elif level == logging.WARNING:
      log.original_warning(modified_message)
  elif level == logging.CRITICAL:
      log.original_critical(modified_message)
def customized_error(message, *args, **kwargs):
  customized_logger(logging.ERROR, message, *args, **kwargs)
def customized_info(message, *args, **kwargs):
  customized_logger(logging.INFO, message, *args, **kwargs)
def customized_debug(message, *args, **kwargs):
  customized_logger(logging.DEBUG, message, *args, **kwargs)
def customized_warning(message, *args, **kwargs):
  customized_logger(logging.WARNING, message, *args, **kwargs)
def customized_critical(message, *args, **kwargs):
  customized_logger(logging.CRITICAL, message, *args, **kwargs)

log.error = customized_error
log.info = customized_info
log.debug = customized_debug
log.warning = customized_warning
log.critical = customized_critical

# Settings
# debug = True
# if debug:
#   Deb_set_printCallstack(True)

# data_tag = "data"

try:
  mount_parent = os.environ['VMM_MOUNT_ROOT']
except Exception as e:
  log.debug(f"{e} - we will continue with `/var/run/vmm`")
  mount_parent = "/var/run/vmm"
try:
  VMM_ZION_PATH = os.environ['VMM_ZION_PATH']
except Exception as e:
  log.debug(f"{e} - we will continue with `/#/zion/k44`")
  VMM_ZION_PATH = "/#/zion/k44"
try:
  VMM_ZVOL_PARENT_PATH = os.environ['VMM_ZVOL_PARENT_PATH']
except Exception as e:
  log.debug(f"{e} - we will continue with `None`")
  VMM_ZVOL_PARENT_PATH = None

# Create the parser
parser = argparse.ArgumentParser(description="virtual machine worker")
subparser = parser.add_subparsers(required=True)

shared_parser = argparse.ArgumentParser(add_help=False)
shared_parser.add_argument("vmname", type=str, help="the name of the vm")
shared_parser.add_argument("-v", "--verbose", default=False, action='store_true', help="print verbose output")
shared_parser.add_argument("-s", "--silent", default=False, action='store_true', help="dont print nixos-output output")
shared_parser.add_argument("--vmorg", type=str, default=None, help="the organisation under which the vm shall be installed")
shared_parser.add_argument("--data_as_dataset", default=False, action='store_true', help="whether data is just a dataset and not a whole (possibly virtual) disk. (implies --no_data_disk)")
shared_parser.add_argument("--no_snapshot", default=False, action='store_true', help="whether to NOT create a snapshot of a vm")
shared_parser.add_argument("--additional_binds", type=str, default=None, help="additional binds that should be mounted. Paths given are relative to the host's root. Example: /new/mountpoint:/existing/path,/new/mountpoint2:/existing/path2")



required_argument_parsers_for_creation_parser = argparse.ArgumentParser(add_help=False)
required_argument_parsers_for_creation_parser.add_argument("--data_disk_only", action='store_true', default=False, help="wether to ONLY create a data disk.")
required_argument_parsers_for_creation_parser.add_argument("--no_data_disk", action='store_true', default=False, help="wether to NOT create a data disk.")

required_argument_parsers_for_install_parser = argparse.ArgumentParser(add_help=False)
required_argument_parsers_for_install_parser.add_argument("--do_not_unmount_afterwards", default=False, action='store_true', help="if this flag is set, vm will not be unmounted after install.")

external_parser = argparse.ArgumentParser(add_help=False)
external_parser.add_argument("--mountpoint", type=str, default=None, help="path to where the nixos installation is (or should be) mounted")
external_parser.add_argument("--division", type=str, default=None, help="a physical host (i.e. usb drive) may have multiple encrypted blockdevs that mirror its data. we support mounting only one for now.")
external_parser.add_argument("--encrypted", default=False, action='store_true', help="if this flag is set, the main and data partitions will be encrypted (or decrypted on mount)")
external_parser.add_argument("--key_file", type=str, default=None, help="path to keyfile for decrypting and encrypting the dm_crypt")

external_parser.add_argument("--main_blockdev", type=str, default=None, help="the main blockdev for an external host (i.e. usb drive)")
external_parser.add_argument("--data_blockdev", type=str, default=None, help="the data blockdev for an external host (i.e. usb drive)")


size_parser = argparse.ArgumentParser(add_help=False)
size_parser.add_argument("--data_disk_size", help="including a unit (10GiB, 1500M, ...)")
size_parser.add_argument("--main_disk_size", help="including a unit (10GiB), 1500M, ...)")



zvol_parser = argparse.ArgumentParser(add_help=False)
zvol_parser.add_argument("--zvol_parent_path", default=VMM_ZVOL_PARENT_PATH, help="the zfs parent path under which to create the block devices")

# Add subparsers
create_parser = subparser.add_parser('create', parents=[shared_parser, zvol_parser, size_parser, external_parser, required_argument_parsers_for_creation_parser], help='checks if the virtual machine already exists, otherwise creates the virtual machine')


mount_parser = subparser.add_parser('mount', parents=[shared_parser, external_parser], help='mount an already existing virtual machine.')
unmount_parser = subparser.add_parser('unmount', parents=[shared_parser], help='unmount an already existing virtual machine.')
resize_parser = subparser.add_parser('resize', parents=[shared_parser, zvol_parser, size_parser], help='resize an already existing virtual machine.')
install_parser = subparser.add_parser('install', parents=[shared_parser, zvol_parser, external_parser, required_argument_parsers_for_install_parser], help='install an already existing virtual machine.')
enter_parser = subparser.add_parser('enter', parents=[external_parser], help='enter an already existing virtual machine.')
kill_parser = subparser.add_parser('kill', parents=[shared_parser], help='kill a running virtual machine (virsh destroy vmname).')
setup_vm_parser = subparser.add_parser('setup_vm', parents=[shared_parser, zvol_parser, size_parser,  external_parser, required_argument_parsers_for_creation_parser, required_argument_parsers_for_install_parser], help='sets up a vm (create and install)')
remove_vm_parser = subparser.add_parser('remove_vm', parents=[shared_parser], help='completely removes the vm from the system')
make_snapshot_parser = subparser.add_parser('snapshot', parents=[shared_parser, zvol_parser], help='snapshots a vm')
#Add arguments to subparsers


enter_parser.add_argument("vmname", type=str, help="the name of the vm")

make_snapshot_parser.add_argument("--snapshot_name", type=str, default="", help="the name of the snapshot")

def is_partitioned(blockdev):
  # -s means script
  # -q means that grep suppresses all output and only returns the exist status
  returncode, formatted_output, formatted_response, formatted_error = exec_for_bool(f"parted -s {blockdev} print")
  return returncode

# returns true if the command succeeds
def exec_for_bool(command, input=None):
  retVal = False
  returncode, formatted_output, formatted_response, formatted_error = exec(command, input)
  if returncode == 0:
    retVal = True
  return retVal, formatted_output, formatted_response, formatted_error

# we are overriding python's internal exec, which would execute python code dynamically, because we don't need nor like it
def myexec(command, input=None):
  log.info(f"Executing command: {command}")
  if verbose:
    process = subprocess.Popen(command,
                            shell=True)
  else:
    process = subprocess.Popen(command,
                            shell=True,
                            stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE)
  if input is not None:
    input_data = ""
    for item in input:
      input_data = input_data + item + "\n"
    process.communicate(input=input_data.encode("utf-8"))
  formatted_output = []
  formatted_response = []
  formatted_error = []
  #set blocking to not blocking is necessary so that readline wont block when the process already finished. this only works on linux systems!
  os.set_blocking(process.stdout.fileno(), False)
  os.set_blocking(process.stderr.fileno(), False)
  try:
    timestamp_last_stdout_readline_start = datetime.now()
    timestamp_last_stderr_readline_start = datetime.now()
    timestamp_last_stdout_readline = timestamp_last_stdout_readline_start
    timestamp_last_stderr_readline = timestamp_last_stderr_readline_start
    while process.poll() is None:
      if process.stdout != None:
        response_line = process.stdout.readline().decode("utf-8").replace("\n", "")
        if not silent and response_line != "":
          log.info("stdout: " + response_line)
        if response_line != "":
          timestamp_last_stdout_readline_start = datetime.now()
          timestamp_last_stdout_readline = timestamp_last_stdout_readline_start
          timestamp_last_stderr_readline = datetime.now()
      if process.stderr != None:
        error_line = process.stderr.readline().decode("utf-8").replace("\n", "")
        if not silent and error_line != "":
          log.info("stderr: " + error_line)
        if error_line != "":
          timestamp_last_stderr_readline_start = datetime.now()
          timestamp_last_stderr_readline = timestamp_last_stderr_readline_start
          timestamp_last_stdout_readline = datetime.now()
      if (process.stderr != None and error_line == "") and (process.stdout != None and response_line == ""):
        timestamp_stdout_now = datetime.now()
        timestamp_stderr_now = datetime.now()
        if timestamp_stderr_now > (timestamp_last_stderr_readline + timedelta(seconds = 5)) and \
          timestamp_stdout_now > (timestamp_last_stdout_readline + timedelta(seconds = 5)):
          no_output_since = min(timestamp_stderr_now - timestamp_last_stderr_readline_start, timestamp_stdout_now - timestamp_last_stdout_readline_start)
          log.warning(f"Command `{command}` had no stderr and stdout output since {no_output_since}.")
          timestamp_last_stdout_readline = timestamp_stdout_now
          timestamp_last_stderr_readline = timestamp_stderr_now
      elif (process.stderr != None and error_line == ""):
        timestamp_stderr_now = datetime.now()
        if timestamp_stderr_now > (timestamp_last_stderr_readline + timedelta(seconds = 5)):
          log.warning(f"Command `{command}` had no stderr output since {timestamp_stderr_now - timestamp_last_stderr_readline_start}.")
          timestamp_last_stderr_readline = timestamp_stderr_now
      elif (process.stdout != None and response_line == ""):
        timestamp_stdout_now = datetime.now()
        if timestamp_stdout_now > (timestamp_last_stdout_readline + timedelta(seconds = 5)):
          log.warning(f"Command `{command}` had no stdout output since {timestamp_stdout_now - timestamp_last_stdout_readline_start}.")
          timestamp_last_stdout_readline = timestamp_stdout_now
      if response_line != "":
        formatted_response.append(response_line)
        formatted_output.append(response_line)
      if error_line != "":
        formatted_error.append(error_line)
        formatted_output.append(error_line)
  except Exception as e:
    pass
  try:
    response = process.stdout.readlines()
    for line in response:
      line = line.decode("utf-8").replace("\n", "")
      if line != "":
        if not silent:
          log.info("stdout: " + line)
        formatted_response.append(line)
        formatted_output.append(line)
  except Exception as e:
    pass
  try:
    error = process.stderr.readlines()
    for line in error:
      line = line.decode("utf-8").replace("\n", "")
      if line != "":
        if not silent:
          log.info("stderr: " + line)
        formatted_error.append(line)
        formatted_output.append(line)
  except Exception as e:
    pass
  return process.returncode, formatted_output, formatted_response, formatted_error
exec = myexec

def exec_or(command, error_message, input=None):
  returncode, formatted_output, formatted_response, formatted_error = exec_for_bool(command, input)
  if not returncode:
    concatenated_message = ""
    for line in formatted_output:
      concatenated_message = concatenated_message + line
      throw(concatenated_message + "\n" + error_message)
  else:
    return returncode, formatted_output, formatted_response, formatted_error

def exec_for_list(command, input=None):
  returncode, formatted_output, formatted_response, formatted_error = exec(command, input)
  return formatted_response

def mkdirs(root, dirs):
  for d in dirs:
    new_directory_name = f"{root}/{d}"
    os.makedirs(new_directory_name, exist_ok=True)
    log.info(f"created directory: {new_directory_name}")

def is_zpool_imported(name):
  log.info(f"checking if zpool `{name}` is already imported...")
  returncode, formatted_output, formatted_response, formatted_error = exec(f"zpool list -H -o name | grep -q --extended-regexp '^{name}$'")
  return returncode == 0

def is_zpool_importable(name):
  returncode, formatted_output, formatted_response, formatted_error = exec(f"zpool import | grep -q --extended-regexp 'pool: {name}$'")
  return returncode == 0

def yes(question):
  log.warning(question + " (type yes):")
  is_sure = input()
  return is_sure == "yes"

def is_zfs_manual_mount(zfs_path):
  returncode, formatted_output, formatted_response, formatted_error = exec(f"zfs get mountpoint {zfs_path} -H -o value")
  if "dataset does not exist" in formatted_output[0]:
    log.warning("dataset does not exist: this just means it is not a legacy mount and instead a normal mount")
    return False
  if "legacy" in formatted_response:
    return True
  else:
    return False

def is_formatted(blockdev):
  returncode, formatted_output, formatted_response, formatted_error = exec(f"blkid {blockdev} | grep -q 'TYPE='")
  return returncode == 0

def is_formatted_as(blockdev, filesystemtype):
  returncode, formatted_output, formatted_response, formatted_error = exec(f"blkid {blockdev} | grep -q 'TYPE=\"{filesystemtype}\"'")
  return returncode == 0

def does_zfs_dataset_exist(zfs_path):
  log.info("checking if zfs exists...")
  returncode, formatted_output, formatted_response, formatted_error = exec_for_bool(f"zfs list {zfs_path} -H -o name")
  return returncode

def does_path_exist(path):
  if os.path.islink(path) or os.path.isfile(path) or os.path.isdir(path):
    return True
  return False

def throw(message):
  log.error(message)
  raise ValueError(message)

def chmods_replace(path, elements, rights):
  for element in elements:

    element_to_be_changed = f"{path}/{element}"
    try:
      # using the command chmod since bit operations are not my thing
      exec(f"chmod {rights} {element_to_be_changed}")
    except Exception as e:
      error_message = f"Could not change file mods, are you root? Error: '{e}'"
      log.error(error_message)
      raise BaseException(error_message)
    log.info(f"modify rights of '{element_to_be_changed}' to '{rights}'")


def is_bind_mounted_as(pointed, pointing):
  pointers = exec_for_list(f"findmnt --noheadings --output source {pointing}")
  regexp_pattern = r'\[/(.*)\]'
  regexp_searcher = re.compile(regexp_pattern)
  for pointer in pointers:
    pointer = pointer.replace("\n", "")
    pointer_stripped = re.sub(regexp_pattern, '', pointer)
    returncode, formatted_output, formatted_response, formatted_error = exec(f"findmnt --noheadings --output source,target {pointer_stripped} --json")
    mount_json_string = ""
    for line in formatted_output:
      mount_json_string = mount_json_string + line
    mounts_json = json.loads(mount_json_string)
    for mount in mounts_json["filesystems"]:
      if "[" in mount["source"]:
        continue
      target_root = mount["target"]
      target_path = regexp_searcher.search(pointer).groups()[0]
      target = os.path.join(target_root, target_path)
      if target == pointed:
        log.info(f"bind pointed: `{pointed}` is already mounted as target: `{target}`")
        return True
  return False

def bind_mount(pointed, pointing):
  #alexTODO: check if this works as expected
  if not is_bind_mounted_as(pointed, pointing):
    log.info(f"pointed: `{pointed}` is not bindmounted on pointing: `{pointing}`.")
    log.info(f"makedirs `{pointing}`")
    os.makedirs(pointing, exist_ok=True)
    exec_or(f"mount --bind '{pointed}' '{pointing}'", f"bind mount failed from (pointing) '{pointing}' to (pointed) '{pointed}' path.")

def mount_additional_binds(list):
  if list != None:
    for mnt in list.split(","):
      r = mnt.split(":")
      if len(r) != 2:
        throw(f"--additional-binds malformatted.")
  else:
    log.info("no additional binds to mount were provided.")



def import_zpool(poolname):
  exec_or(f"zpool import -f {poolname} -R {vmroot}", f"unable to import existing zpool {vmname}. Please destroy, make unavailable or import manually to proceed.")

def get_mountpoints(blockdev_or_zfs_path):
  return exec_for_list (f"findmnt --noheadings --output target {blockdev_or_zfs_path}")

def get_bind_mountpoints(pointer):
  return exec_for_list(f"findmnt --noheadings --output source {pointer}")

def is_mounted_as(blockdev, mount_path):
  paths = get_mountpoints(blockdev)
  for path in paths:
    if mount_path in path:
      return True
  return False

def is_mounted(blockdev):
  list = get_mountpoints(blockdev)
  return len(list) != 0


def get_or_create_blockdev(vol_name, disk_size, args):
  if getattr(args, f"{vol_name}_blockdev") is not None:
    return getattr(args, f"{vol_name}_blockdev")
  else:
    log.info(f"no --{vol_name}_blockdev given as argument. Trying to create zvol...")
    zvol_path = f"{get_zvol_parent_path(args)}/vm-{vmname}-{vol_name}"
    blockdev_path = get_or_create_zvol(vol_name, disk_size, zvol_path)
    return blockdev_path


def get_or_create_zvol(vol_name, disk_size, zvol_path):
  if not does_zfs_dataset_exist(zvol_path):
    log.info(f"creating zfs blockdev for {vol_name}]-disk...")
    create_zvol(vol_name, disk_size, zvol_path)
  else:
    log.info(f"zfs blockdev for {vol_name}-disk already exists")
  blockdev_path = f"/dev/zvol/{zvol_path}"
  return blockdev_path



def create_zvol(vol_name, disk_size, zvol_path):
  log.info(f"creating {vol_name} disk: {zvol_path}")

  exec_or(f"zfs create {zvol_path} -V {disk_size}", f"could not create {vol_name} disk: {zvol_path}")
  refresh_partitions()

def refresh_partitions():
  exec("udevadm trigger -v --subsystem-match=block '--sysname-match=zd*' --action=change")
  exec("udevadm settle")
  exec("partprobe")

def check_is_partitioned(blockdev, which):
  if is_partitioned(blockdev):
    log.warning(f"{blockdev} is already partitioned. Please destroy the partition table of `{which}`-disk manually if you want me to recreate it. Don't forget to wipefs or else you'll confuse me.")
    return True
  else:
    return False

def possibly_partition_main_disk(blockdev):
  log.info(f"checking if `{blockdev}` is already partitioned...")
  if not check_is_partitioned(blockdev, "main"):
    log.info(f"partitioning main disk: {blockdev}")
    error_message = f"could not format {blockdev}"
    exec_or(f"parted {blockdev} -- mklabel gpt", error_message)
    exec_or(f"parted {blockdev} -- mkpart {vmname}-boot 0% 1GiB", error_message)
    exec_or(f"parted {blockdev} -- set 1 boot on", error_message)
    exec_or(f"parted {blockdev} -- mkpart {vmname}-main 1GiB 100%", error_message)
    refresh_partitions()
  else:
    log.info(f"`{blockdev}` is already partitioned.")

def possibly_partition_data_disk(blockdev):
  log.info(f"checking if `{blockdev}` is already partitioned...")
  if not check_is_partitioned(blockdev, "data"):
    log.info(f"`{blockdev}` is not yet partitioned.")
    log.info(f"partitioning data disk: {blockdev}")
    error_message = f"could not format {blockdev}"
    exec_or(f"parted {blockdev} -- mklabel gpt", error_message)
    exec_or(f"parted {blockdev} -- mkpart {vmname}-data 0% 100%", error_message)
    refresh_partitions()
  else:
    log.info(f"`{blockdev}` is already partitioned.")

def zpool_ensure_import_if_importable(vmname):
  if not is_zpool_imported(vmname):
    log.info(f"zpool `{vmname}` is not yet imported.")
    if is_zpool_importable(vmname):
      log.info(f"zpool `{vmname}` is importable. trying to import zpool `{vmname}`...")
      import_zpool(vmname)
      log.info(f"zpool `{vmname}` imported. we assume that everything has been partitioned properly")
      return True
    else:
      return False
  else:
    return True

def classic_mount_if_not_mounted(partition, path):
  if not is_mounted_as(partition, f"{path}"):
    log.info("mounting partition")
    exec_or(f"mount {partition} {path}", f"failed to mount partition: `{partition}`")
    log.info(f"mounted `{partition} {path}`")



def get_size(usersize, defaultsize):
  size = defaultsize
  if usersize is not None:
    size = usersize
  return size

def ask_user_for_password():
  pw = getpass("please enter the password for the dm-crypt: ")
  return pw


def handle_dmcrypt(volname, partition, allow_create=False):
  if args.encrypted:
    crypt_name = f"{vmname}-{volname}"
    if does_path_exist(f"/dev/mapper/{crypt_name}"):
      log.info("dmcrypt already opened")
    else:
      pws = None
      key_file_arg = ""
      if args.key_file is not None:
        key_file_arg = f" --key-file {args.key_file}"
      else:
        pw = ask_user_for_password()
        pws = [pw, pw, ""]
      log.info("trying to decrypt blockdev with luks")
      returncode, formatted_output, formatted_response, formatted_error = exec(f"cryptsetup open {partition} {crypt_name} {key_file_arg}", input = pws)
      is_not_a_dm_crypt_device = False
      for line in formatted_output:
        if "doesn't appear to be a valid" in line:
          is_not_a_dm_crypt_device = True
      if is_not_a_dm_crypt_device:
        if allow_create:
          log.info("it does not appear to be luks encrypted yet. formatting blockdev with luks...")
          exec_or(f"cryptsetup luksFormat --allow-discards {partition} {key_file_arg}", f"could not format luks encrypted partition", input = pws)
          exec_or(f"cryptsetup open {partition} {crypt_name} {key_file_arg}", f"could not decrypt the partition I just formatted. this is weird", input = pws)
        else:
          raise ValueError(f"not an encrypted partition: {partition}")
    return f"/dev/mapper/{crypt_name}"
  else:
    return partition

def create(args):
  guard_vm_running(vmname)



  partition_prefix = f"/dev/disk/by-partlabel/{vmname}{division_arg}"

  if not args.data_disk_only:


    log.info("check if main zpool is imported...")
    if zpool_ensure_import_if_importable(vmname):
      log.info(f"zpool `{vmname}` is imported.")
    else:
      log.info("zpool is not importable.")
      main_partition_blockdev = f"{partition_prefix}-main"
      log.info(f"does zfs blockdev `{main_partition_blockdev}` exist...")
      if not does_path_exist(main_partition_blockdev):
        log.info(f"zfs blockdev `{main_partition_blockdev}` does not exist.")

        blockdev_path = get_or_create_blockdev("main", get_size(args.main_disk_size, "10GiB"), args)

        possibly_partition_main_disk(blockdev_path)
        log.info(f"zfs blockdev `{main_partition_blockdev}` created.")
      else:
        log.info(f"zfs blockdev `{main_partition_blockdev}` exists.")

      decrypted_blockdev = handle_dmcrypt(f"main", main_partition_blockdev, allow_create=True)
      exec_or(f"zpool create {vmname} -R {vmroot} {decrypted_blockdev} -o autotrim=on -O acltype=posix -O atime=off -O canmount=off -O dnodesize=auto -O utf8only=on -O xattr=sa -O mountpoint=none", f"could not create zpool: {vmname}")

    # for main, we need this, but data wont have this, see below
    if not does_zfs_dataset_exist(f"{vmname}/fsroot"):
      log.info(f"creating zfs: {vmname}/fsroot")
      exec_or(f"zfs create {vmname}/fsroot -o mountpoint=legacy -o normalization=formD", f"could not create zfs dataset: {vmname}/fsroot")
    else:
      log.info(f"zfs {vmname}/fsroot already exists")



    mkdirs(vmroot, ".")


    if is_zfs_manual_mount(f"{vmname}/fsroot"):
      log.info(f"mount zfs '{vmname}/fsroot' manually...")
      returncode, formatted_output, formatted_response, formatted_error = exec(f"mount -t zfs {vmname}/fsroot {vmroot}")
      if 0 != returncode:
        if not yes(f"could not mount zfs dataset: `{vmname}/fsroot`. Error: `{formatted_error[0]}` Do you want to continue?"):
          exit()

    mkdirs(f"{vmroot}", ["boot", "root", "etc", "nix", "data", "home"])
    chmods_replace(f"{vmroot}", ["etc", "nix", "data", "home"], 755)

    log.info("checking boot partition")

    boot_partition = f"{partition_prefix}{division_arg}-boot"
    if not is_formatted(boot_partition):
      log.info(f"formatting '{boot_partition}'")
      exec_or(f"mkfs.fat -F 32 -n \"{(vmname+division_arg)[0:6]}-boot\" {boot_partition}", f"could not format: {boot_partition}")
    else:
      log.warning(f"partition `{boot_partition}` is already formatted. You can set the flag `--reformat-boot-partition` to reformat it.")

    classic_mount_if_not_mounted(boot_partition, f"{vmroot}/boot")


  create_data_disk = not args.no_data_disk

  if args.data_as_dataset:
    log.info("data is dataset, checking data dataset")
    # create data as a dataset
    create_data_disk = False
    returncode, formatted_output, formatted_response, formatted_error = exec_for_bool(f"zfs create {vmname}/data -o mountpoint=/data -o com.sun:auto-snapshot=true")
    if not does_zfs_dataset_exist(f"{vmname}/data") and not returncode:
      throw(f"failed to create zfs dataset: {vmname}/data")


  if create_data_disk:
    log.info("creating data disk (if necessary)")
    # create data disk
    data_pool = f"{vmname}-data"

    log.info(f"checking if zpool `{data_pool}` is not imported...")
    if zpool_ensure_import_if_importable(data_pool):
      log.info(f"zpool `{data_pool}` is imported.")
    else:
      log.info("zpool is not importable.")
      data_partition_blockdev = f"{partition_prefix}-data"
      log.info(f"checking if zfs blockdev `{data_partition_blockdev}` exists...")
      if not does_path_exist(data_partition_blockdev):
        log.info(f"zfs blockdev `{data_partition_blockdev}` does not exist. trying to create...")
        blockdev_path = get_or_create_blockdev("data", get_size(args.data_disk_size, "4GiB"), args)
        possibly_partition_data_disk(blockdev_path)
        log.info(f"zfs blockdev `{data_partition_blockdev}` created.")
      else:
        log.info(f"zfs blockdev `{data_partition_blockdev}` exists.")
      log.info(f"create zpool `{data_pool} `...")
      decrypted_blockdev = handle_dmcrypt(f"data", data_partition_blockdev, allow_create=True)
      exec_or(f"zpool create {data_pool} -R /var/vmm/{data_pool} {decrypted_blockdev} -o autotrim=on -O acltype=posix -O atime=off -O dnodesize=auto -O utf8only=on -O xattr=sa -O mountpoint=/data -O com.sun:auto-snapshot=true", f"could not create zpool: {data_pool}")
      log.info(f"zpool `{data_pool}` created.")

  data_pool_location = f"{vmroot}/data"
  mkdirs(f"{data_pool_location}", ["root", "home"])
  chmods_replace(f"{data_pool_location}", [".", "home"], 755)
  chmods_replace(f"{data_pool_location}", ["root"], 700)
  bind_mount(f"{data_pool_location}/root", f"{vmroot}/root")
  bind_mount(f"{data_pool_location}/home", f"{vmroot}/home")
  mount_additional_binds(args.additional_binds)

def legacy_mount_zfs(zfs_path, fs_path, allow_failure=False):
  if not is_mounted_as(zfs_path, fs_path):
    returncode, formatted_output, formatted_response, formatted_error = exec_for_bool(f"mount -t zfs {zfs_path} {fs_path}")
    if len(formatted_output) == 0:
      return
    if "is already mounted" in formatted_output[0]:
      return
    if "cannot be mounted" in formatted_output[0] and not allow_failure:
      error_message = formatted_output[0]
      log.error(error_message)
      raise BaseException(error_message)
    if not returncode and not allow_failure:
      error_message = f"failed to mount zfs: `{zfs_path}` @ `{fs_path}`"
      log.error(error_message)
      raise BaseException(error_message)

def mount_zfs(zfs_path, allow_failure=False):
  #
  returncode, formatted_output, formatted_response, formatted_error = exec_for_bool(f"zfs mount {vmname}/data")

def is_vm_running(vmname):
  # --name: return only the name
  # -q: no output, only exit code for success or failure
  returncode, formatted_output, formatted_response, formatted_error = exec_for_bool(f"virsh list --name | grep -q --extended-regexp '^{vmname}$'")
  return returncode

def guard_vm_running(vmname):
  vm_was_running = False
  if is_vm_running(vmname):
    vm_was_running = True
    if yes(f"VM `{vmname}` is currently up and running. Do you want to shut it down?"):
      exec(f"virsh shutdown {vmname}")
      time.sleep(10)
      if is_vm_running(vmname):
        if yes(f"VM `{vmname}` is still running, do you want to kill it? (you can wait some more before you hit enter)"):
          exec_or(f"virsh destroy {vmname}", f"failed to kill vm {vmname}")
        else:
          throw(f"exiting...")
      log.info(f"have shut down vm '{vmname}'")
    else:
      throw(f"exiting...")
  return vm_was_running

def mount_legacy_if_zfs_is_legacy_mount(zfs_path, fs_path):
  if is_zfs_manual_mount(zfs_path):
    legacy_mount_zfs(f"{zfs_path}", f"{fs_path}")


def mount(args):
  guard_vm_running(vmname)
  log.info(f"mounting host '{vmname}'...")
  if not os.path.isdir(f"{vmroot}"):
    os.makedirs(f"{vmroot}", exist_ok=True)

  partition_prefix = f"/dev/disk/by-partlabel/{vmname}{division_arg}"

  if zpool_ensure_import_if_importable(vmname):
    log.info(f"zpool `{vmname}` is imported.")
  else:
    error_message = f"main zpool `{vmname}` is not importable."
    log.error(error_message)
    raise BaseException(error_message)
  mount_legacy_if_zfs_is_legacy_mount(f"{vmname}/fsroot", f"{vmroot}")


  data_dir = f"{vmroot}/data"
  if args.data_as_dataset:
    mount_legacy_if_zfs_is_legacy_mount(f"{vmname}/data", f"{vmroot}/data")

  else:
    data_pool = f"{vmname}-data"

    log.info(f"checking if data dataset of `{data_pool}` already exists...")
    if does_zfs_dataset_exist(data_pool):
      mount_legacy_if_zfs_is_legacy_mount(f"{vmname}/data", f"{data_dir}")
    else:
      log.info(f"data dataset of `{data_pool}` does not exists.")
      log.info(f"checking if data zpool `{data_pool}` is imported...")
      if zpool_ensure_import_if_importable(data_pool):
        log.info(f"zpool `{data_pool}` is imported.")
      else:
        error_message = f"data zpool `{data_pool}` is not importable."
        log.error(error_message)
        raise BaseException(error_message)

  mount_legacy_if_zfs_is_legacy_mount(f"{vmname}/etc", f"{vmroot}/etc")
  mount_legacy_if_zfs_is_legacy_mount(f"{vmname}/nix", f"{vmroot}/nix")

  boot_partition = f"{partition_prefix}-boot"
  mkdirs(f"{data_dir}", ["root", "home"])
  classic_mount_if_not_mounted(boot_partition, f"{vmroot}/boot")
  bind_mount(f"{data_dir}/root", f"{vmroot}/root")
  bind_mount(f"{data_dir}/home", f"{vmroot}/home")
  mount_additional_binds(args.additional_binds)

def unmount(args):
  guard_vm_running(vmname)
  log.info(f"unmounting host `{vmname}`...")
  # chronological order for zpool export required
  returncode, formatted_output, formatted_response, formatted_error = exec(f"umount -R /var/vmm/{vmname}/boot")
  if len(formatted_output) > 0 and "not mounted" in formatted_output[0]:
      error_message = formatted_output[0]
      log.warning(error_message)
  if len(formatted_output) > 0 and "target is busy" in formatted_output[0]:
      error_message = formatted_output[0] + "\n are you maybe in some folder inside the device, or do you have any files from there open?"
      log.error(error_message)
      raise BaseException(error_message)
  returncode, formatted_output, formatted_response, formatted_error = exec(f"umount -R /var/vmm/{vmname}")
  if len(formatted_output) > 0 and "not mounted" in formatted_output[0]:
      error_message = formatted_output[0]
      log.warning(error_message)
  if len(formatted_output) > 0 and "target is busy" in formatted_output[0]:
      error_message = formatted_output[0] + "\n are you maybe in some folder inside the device, or do you have any files from there open?"
      log.error(error_message)
      raise BaseException(error_message)
  returncode, formatted_output, formatted_response, formatted_error = exec(f"zpool export {vmname}-data")
  if len(formatted_output) > 0 and ("unmount failed" in formatted_output[0] or "pool is busy" in formatted_output[0]):
      error_message = formatted_output[0]
      log.error(error_message)
      raise BaseException(error_message)
  returncode, formatted_output, formatted_response, formatted_error = exec(f"umount -R /var/vmm/{vmname}")
  if len(formatted_output) > 0 and "not mounted" in formatted_output[0]:
      log.warning("Error: " + formatted_output[0] + " - was not mounted, but its okay, we expected this.")
  if len(formatted_output) > 0 and "pool or dataset busy" in formatted_output[0]:
      error_message = formatted_output[0]
      log.error(error_message)
      raise BaseException(error_message)
  returncode, formatted_output, formatted_response, formatted_error = exec(f"zpool export {vmname}")
  if len(formatted_output) > 0 and "pool or dataset busy" in formatted_output[0]:
      error_message = formatted_output[0]
      log.error(error_message)
      raise BaseException(error_message)

def resize(args):
  guard_vm_running(vmname)
  #alexTODO: is it mounted? no required
  #unmount? yes
  blockdev = f"/dev/zvol/{get_zvol_parent_path(args)}/"
  raise NotImplementedError

def get_zvol_parent_path(args):
  if args.zvol_parent_path is None:
    raise ValueError("argument --zvol_parent_path or environment variable VMM_ZVOL_PARENT_PATH is required to be set for this operation.")
  return args.zvol_parent_path

def install(args):
  guard_vm_running(vmname)
  # log.info("start mounting...")
  # mount(args)
  # log.info("mounting finished. installing...")
  exec_or(f"mountpoint {vmroot}", f"vmroot ({vmroot}) is not a mountpoint.")
  
  if not args.no_snapshot:
    create_snapshot(vmname, "auto_snapshot_before_install")
  vmorg = args.vmorg
  if vmorg is None:
    raise ValueError("argument --vmorg required")
  returncode, install_output, install_result, install_error = exec_or(f"cd {VMM_ZION_PATH}; echo PATH: $PATH; echo NIX_PATH: $NIX_PATH; nixos-install --flake ./{vmorg}/hosts/{vmname}#{vmname} --root {vmroot} --impure --no-root-passwd", "nixos-install failed. Maybe you need to `set NIX_PATH=...`? Or maybe check if you are sure, that the nix configuration file does exist and is properly implemented?")
  if not isinstance(install_result, list):
    install_result = [install_result]
  install_result_string = ""
  for line in install_result:
    install_result_string = install_result_string + line
    if len(install_result) == 1 and "configuration file" in line and "doesn't exist" in line:
      error_message = line + f"\nMaybe you did not checkin the nix files into git? In order for install to work, the .nix file and all of the config files for your new server `{vmname}` must exist in `/#/zion/k44/feu/hosts/{vmname}` and those files must be commited to git, so that nixos-install can find them."
      log.error(error_message)
      raise BaseException(error_message)
  install_error_string = ""
  for line in install_error:
    install_error_string = install_error_string + line
    if f"error: attribute '{vmname}' missing" in line:
      error_message = line + f"\nMaybe the NIX_PATH is not set properly? e.g. '/#/zion/k44/knet' should probably be not in there and you have to remove it!\n\nAlso make sure you have added `{vmname}` to /#/zion/k44/feu/common/organisation.nix -> hosts!"
      log.error(error_message)
      raise BaseException(error_message)
  if not args.do_not_unmount_afterwards:
    unmount(args)

  if not args.no_snapshot:
    create_snapshot(vmname, "auto_snapshot_after_install")

def make_snapshot(args):
  create_snapshot(args.snapshot_name)

def create_snapshot(snapshot_name = ""):
  # TODO: I can't find this function. We must create some library we can include.
  ##  now = Get_timestamp_for_filenames()
  # hence I replaced it with:
  now = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
  if snapshot_name != "":
    # add underscore as separator before snapshot_name if snapshot_name shall be used
    snapshot_name = "_" + snapshot_name
  vm_data = f"vm-{vmname}-data"
  vm_vda = f"vm-{vmname}-vda"
  data_snapshot_name = f"{vm_data}@{now}{snapshot_name}"
  vda_snapshot_name = f"{vm_vda}@{now}{snapshot_name}"

  data_snapshot_path = os.path.join(get_zvol_parent_path(args), data_snapshot_name)
  vda_snapshot_path = os.path.join(get_zvol_parent_path(args), vda_snapshot_name)
  log.info(f"creating snapshot `{data_snapshot_path}`...")
  exec_or(f"zfs snapshot {data_snapshot_path}", f"Failed to save snapshot to {data_snapshot_path}.")
  log.info(f"snapshot `{data_snapshot_path}` created.")
  log.info(f"creating snapshot `{vda_snapshot_path}`...")
  exec_or(f"zfs snapshot {vda_snapshot_path}", f"Failed to save snapshot to {vda_snapshot_path}.")
  log.info(f"snapshot `{vda_snapshot_path}` created.")

#alexTODO: new function clear delete all vmm-auto-snapshots

#alexTODO: start function
# check if already running
# if not running:
#   check if root is mounted
#     then unmount
#     if unmount disk error: exit
#     if unmount disk ok: start vm
#   else root not mounted: start vm
def start(args):
  log.info(f"starting vm `{vmname}`...")
  returncode, install_output, install_result, install_error = exec_or(f"virsh start {vmname}", f"failed to start vm `{vmname}`. Did you just setup a new vm? then you probably have to rebuild eva first! And then reboot eva...")
  log.info(f"vm `{vmname}` started.")



#alexTODO: snapshot function

#alexTODO: reverse-to-last-snapshot-before-install
#zfs rollback eva/vms/vm-banah-data@2024-12-15_22-08-30
#zfs rollback eva/vms/vm-banah-vda@2024-12-15_22-08-44

#alexTODO: reverse-to-last-snapshot-after-install



#alexTODO: stop function with "shutdown?yes"

def kill(args):
  returncode, formatted_output, formatted_response, formatted_error = exec(f"virsh destroy {vmname}")
  if len(formatted_output) > 0 and returncode != 0:
      error_message = ""
      for line in formatted_output:
        error_message = error_message + "\n" + line
      log.error(error_message)
      raise BaseException(error_message)

#alexTODO: list vms (virsh list --all)


def setup_wireguard():
  data_pool_location = f"{vmroot}/{data_tag}"
  keys_path = os.path.join(data_pool_location, "keys")
  wireguard_path = os.path.join(keys_path, "wireguard")
  feu_wireguard_path =  os.path.join(wireguard_path, "feu")
  knet_wireguard_path =  os.path.join(wireguard_path, "knet")
  mkdirs("", [keys_path, wireguard_path, feu_wireguard_path, knet_wireguard_path])
  chmods_replace("", [keys_path], 555)
  chmods_replace("", [wireguard_path, feu_wireguard_path, knet_wireguard_path], 550)
  privatekey_path =  os.path.join(wireguard_path, "privatekey")
  publickey_path =  os.path.join(wireguard_path, "publickey")
  if not os.path.isfile(privatekey_path):
    exec_or(f"wg genkey | tee {privatekey_path} | wg pubkey > {publickey_path}", "failed to generade wireguard private and public key")
  #choosing systemd-network group for key files only works because the userid of systemd-network on eva is (should be) the same as on the newly created server
  exec_or(f"chgrp -R systemd-network {wireguard_path}", "failed to change group to systemd-network")
  g_psk_path = os.path.join(feu_wireguard_path, "_g.psk")
  if not os.path.isfile(g_psk_path):
    exec_or(f"wg genpsk > {g_psk_path}", "failed to generate preshared key for _g")
  returncode, g_presharedkey, formatted_response, formatted_error = exec_or(f"cat {g_psk_path}", "could not open preshared keyfile of _g")
  k_psk_path = os.path.join(knet_wireguard_path, "_k.psk")
  if not os.path.isfile(k_psk_path):
    exec_or(f"wg genpsk > {k_psk_path}", "failed to generate preshared key for _k")
  returncode, k_presharedkey, formatted_response, formatted_error = exec_or(f"cat {k_psk_path}", "could not open preshared keyfile of _k")
  returncode, publickey, formatted_response, formatted_error = exec_or(f"cat {publickey_path}", "could not open public key")
  chmods_replace("", [keys_path], 555)
  chmods_replace("", [wireguard_path, feu_wireguard_path], 550)
  exec_or(f"chgrp -R systemd-network {wireguard_path}", "failed to change group to systemd-network")
  return_string = f"_g Preshared Key:\n{g_presharedkey[0]}\n_k Preshared Key:\n{k_presharedkey[0]}\nPublickey:\n{publickey[0]}"
  return return_string


def setup_vm(args):
  guard_vm_running(vmname)
  create(args)
  unmount(args)
  install(args)
  mount(args)
  wireguard_key_string = setup_wireguard()
  unmount(args)
  start(args)
  log.warning(f"Remember to set the keys in `wireguard/feu/{vmname}.conf`:\n{wireguard_key_string}")

def remove_vm(args):
  yes(f"Do you really want to remove the vm `{vmname}` from the system? (remove mounts, remove from virsh, delete disks)")
  yes(f"Are you really sure you want to remove the vm `{vmname}` from the system?")
  guard_vm_running(vmname)
  unmount(args)
  exec(f"virsh undefine --nvram {vmname} --remove-all-storage")
  exec(f"zfs destroy -r eva/vms/vm-{vmname}-vda")
  exec(f"zfs destroy -r eva/vms/vm-{vmname}-data")
  exec(f"rm -rf /var/vmm/{vmname}")
  exec(f"rm -rf /var/vmm/{vmname}-data")




create_parser.set_defaults(func=create)
mount_parser.set_defaults(func=mount)
unmount_parser.set_defaults(func=unmount)
resize_parser.set_defaults(func=resize)
install_parser.set_defaults(func=install)
kill_parser.set_defaults(func=kill)
setup_vm_parser.set_defaults(func=setup_vm)
remove_vm_parser.set_defaults(func=remove_vm)
make_snapshot_parser.set_defaults(func=make_snapshot)




args = parser.parse_args()
vmname = args.vmname

division_arg = ""
if hasattr(args, "division") and args.division is not None:
  division_arg = f"-{args.division}"
vmroot = args.mountpoint
if vmroot == None:
  vmroot = f"{mount_parent}/{vmname}"
verbose = args.verbose
silent = args.silent
returncode, formatted_output, formatted_response, formatted_error = exec("whoami")
try:
  if formatted_output[0] != "root":
    error_message = "You must be root!"
    raise BaseException(error_message)
  args.func(args)
except BaseException as exception:
  error_message = str(traceback.format_exc()) + "\n" + str(exception)

  log.error(error_message)
log.info("vmm finished!")
