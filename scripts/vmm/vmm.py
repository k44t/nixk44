import os, stat, os.path
import shutil
import re
import time
import subprocess
import json
from natsort import natsorted
from datetime import datetime, timedelta

import argparse
import logging
import sys


# Configure the root logger
logging.basicConfig(
  level=logging.DEBUG,
  format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
  handlers=[
    # logging.FileHandler(logfile_path + datetime.now().strftime("%d-%m-%Y_%H:%M:%S.%f") ),  # File handler
    logging.StreamHandler(sys.stdout)   # Stream handler for stdout
  ]
)

log = logging.getLogger("vmm")

def Log_no_header(msg):
  '''I have no idea what this function is supposed to do. So I'll simply replace it with a warning. TODO: Fixme'''
  log.warning("Log_no_header: " + msg)

# TODO: fixme:
# from utils_python.utils_python_package.src.Apoeschllogging import *

# Settings
# debug = True
# if debug:
#   Deb_set_printCallstack(True)

data_tag = "data"

try:
  mount_parent = os.environ(['K44_VMM_MOUNT_ROOT'])
except Exception as e:
  log.warning(f"{e} - we will continue with `/var/vmm`")
  mount_parent = "/var/vmm"
try:
  K44_VMM_ZION_PATH = os.environ(['K44_VMM_ZION_PATH'])
except Exception as e:
  log.warning(f"{e} - we will continue with `/#/zion/k44`")
  K44_VMM_ZION_PATH = "/#/zion/k44"
try:
  K44_VMM_ZVOL_PARENT_PATH = os.environ(['K44_VMM_ZVOL_PARENT_PATH'])
except Exception as e:
  log.warning(f"{e} - we will continue with `None`")
  K44_VMM_ZVOL_PARENT_PATH = None

# Create the parser
parser = argparse.ArgumentParser(description="virtual machine worker")
parser.add_argument("-v", "--verbose", default=False, action='store_true', help="print verbose output")
parser.add_argument("-s", "--silent", default=False, action='store_true', help="dont print nixos-output output")

subparser = parser.add_subparsers(required=True)

shared_parser = argparse.ArgumentParser(add_help=False)
shared_parser.add_argument("vmname", type=str, help="the name of the vm")

vmorg_parser = argparse.ArgumentParser(add_help=False)
vmorg_parser.add_argument("--vmorg", required=True, type=str, help="the organisation under which the vm shall be installed")

required_argument_parsers_for_creation_parser = argparse.ArgumentParser(add_help=False)
required_argument_parsers_for_creation_parser.add_argument("--data_disk_only", help="wether to ONLY create a data disk.")
required_argument_parsers_for_creation_parser.add_argument("--data_as_dataset", help="whether data is just a dataset and not a whole (possibly virtual) disk")
required_argument_parsers_for_creation_parser.add_argument("--no_data_disk", help="wether to NOT create a data disk.")

required_argument_parsers_for_install_parser = argparse.ArgumentParser(add_help=False)
required_argument_parsers_for_install_parser.add_argument("--do_not_unmount_afterwards", default=False, action='store_true', help="if this flag is set, vm will not be unmounted after install.")

external_parser = argparse.ArgumentParser(add_help=False)
external_parser.add_argument("--path", type=str, help="path to where the nixos installation is mounted")

size_parser = argparse.ArgumentParser(add_help=False)
size_parser.add_argument("--data_disk_size", help="including a unit (10GiB, 1500M, ...)")
size_parser.add_argument("--main_disk_size", help="including a unit (10GiB), 1500M, ...)")

mountpoint_parser = argparse.ArgumentParser(add_help=False)
mountpoint_parser.add_argument("--additional_binds", type=str, default=None, help="additional binds that should be mounted. Paths given are relative to the host's root. Example: /new/mountpoint:/existing/path,/new/mountpoint2:/existing/path2")

divison_parser = argparse.ArgumentParser(parents=[mountpoint_parser], add_help=False)
divison_parser.add_argument("--division", type=str, help="the suffix of a mirrored pool we are mounting (for a physical host)")

zvol_parser = argparse.ArgumentParser(add_help=False)
zvol_parser.add_argument("--zvol_parent_path", default=K44_VMM_ZVOL_PARENT_PATH, help="the zfs parent path under which to create the block devices")

# Add subparsers
create_parser = subparser.add_parser('create', parents=[shared_parser, zvol_parser, size_parser, mountpoint_parser, required_argument_parsers_for_creation_parser], help='checks if the virtual machine already exists, otherwise creates the virtual machine')
mount_parser = subparser.add_parser('mount', parents=[shared_parser, divison_parser], help='mount an already existing virtual machine.')
unmount_parser = subparser.add_parser('unmount', parents=[shared_parser], help='unmount an already existing virtual machine.')
resize_parser = subparser.add_parser('resize', parents=[shared_parser, zvol_parser, size_parser], help='resize an already existing virtual machine.')
install_parser = subparser.add_parser('install', parents=[shared_parser, zvol_parser, external_parser, divison_parser, vmorg_parser, required_argument_parsers_for_install_parser], help='install an already existing virtual machine.')
enter_parser = subparser.add_parser('enter', parents=[external_parser], help='enter an already existing virtual machine.')
kill_parser = subparser.add_parser('kill', parents=[shared_parser], help='kill a running virtual machine (virsh destroy vmname).')
setup_vm_parser = subparser.add_parser('setup_vm', parents=[shared_parser, zvol_parser, size_parser,  external_parser, divison_parser, vmorg_parser, required_argument_parsers_for_creation_parser, required_argument_parsers_for_install_parser], help='sets up a vm (create and install)')
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

# returns true if the command succe
def exec_for_bool(command):
  retVal = False
  returncode, formatted_output, formatted_response, formatted_error = exec(command)
  if returncode == 0:
    retVal = True
  return retVal, formatted_output, formatted_response, formatted_error

# we are overriding python's internal exec, which would execute python code dynamically, because we don't need nor like it
def myexec(command):
  log.info(f"Executing command: {command}")
  if verbose:
    process = subprocess.Popen(command, 
                            shell=True)
  else:
    process = subprocess.Popen(command, 
                            shell=True,
                            stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE)
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
          Log_no_header("stdout: " + response_line)
        if response_line != "":
          timestamp_last_stdout_readline_start = datetime.now()
          timestamp_last_stdout_readline = timestamp_last_stdout_readline_start
          timestamp_last_stderr_readline = datetime.now()
      if process.stderr != None:
        error_line = process.stderr.readline().decode("utf-8").replace("\n", "")
        if not silent and error_line != "":
          Log_no_header("stderr: " + error_line)
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
          Log_no_header("stdout: " + line)
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
          Log_no_header("stderr: " + line)
        formatted_error.append(line)
        formatted_output.append(line)
  except Exception as e:
    pass
  return process.returncode, formatted_output, formatted_response, formatted_error
exec = myexec

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
    resulting_right = 0
    for right in rights:
      resulting_right = resulting_right | right
    element_to_be_changed = f"{path}/{element}"
    try:
      os.chmod(element_to_be_changed, right)
    except Exception as e:
      error_message = f"Could not change file mods, are you root? Error: '{e}'"
      log.error(error_message)
      raise BaseException(error_message)
    log.info(f"modify rights of '{element_to_be_changed}' to '{resulting_right}'")

def chmods_add(path, elements, rights):
  for element in elements:
    resulting_right = 0
    for right in rights:
      resulting_right = resulting_right | right
    element_to_be_changed = f"{path}/{element}"
    try:
      st = os.stat(element_to_be_changed)
      os.chmod(element_to_be_changed, st.st_mode | right)
    except Exception as e:
      error_message = f"Could not change file mods, are you root? Error: '{e}'"
      log.error(error_message)
      raise BaseException(error_message)
    log.info(f"modify rights of '{element_to_be_changed}' to '{resulting_right}'")

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

def exec_or(command, error_message):
  returncode, formatted_output, formatted_response, formatted_error = exec_for_bool(command)
  if not returncode:
    concatenated_message = ""
    for line in formatted_output:
      concatenated_message = concatenated_message + line
      throw(concatenated_message + "\n" + error_message)
  else:
    return returncode, formatted_output, formatted_response, formatted_error

def exec_for_list(command):
  returncode, formatted_output, formatted_response, formatted_error = exec(command)
  return formatted_response
  
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

def yield_blockdev_path(which, defaultsize, usersize, zvol_path):
  if not does_zfs_dataset_exist(zvol_path):
    log.info(f"creating zfs blockdev for {which}]-disk...")
    create_blockdev(which, defaultsize, usersize, zvol_path)
  else:
    log.info(f"zfs blockdev for {which}-disk already exists")
  blockdev_path = f"/dev/zvol/{zvol_path}"
  return blockdev_path

def create_blockdev(which, defaultsize, usersize, zvol_path):
  log.info(f"creating {which} disk: {zvol_path}")
  size = defaultsize
  if usersize != None:
    size = usersize
  exec_or(f"zfs create {zvol_path} -V {size}", f"could not create {which} disk: {zvol_path}")
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

def classic_mount_if_not_mounted(partition, path, blockdev_path):
  if not is_mounted_as(partition, f"{path}"):
    log.info("mounting partition")
    exec_or(f"mount {partition} {path}", f"failed to mount partition: `{blockdev_path}`")
    log.info(f"mounted `{partition} {path}`")


def create(args):
  guard_vm_running(vmname)
  if args.zvol_parent_path == None:
      # TODO: is the create function supposed to bring the machine into its final state? (even if it already exists?)
      # k: I think that's the point
      # so this error should only be sent to the user, in case the create function actually has to create something
    log.error("ERROR: the following arguments are required: --zvol_parent_path")
    return

  

  partition_prefix = f"/dev/disk/by-partlabel/{vmname}"
  
  if not args.data_disk_only:

      # create main disk
    log.info("creating main disk (if neccessary)")


  
    zvol_path = f"{args.zvol_parent_path}/vm-{vmname}-vda"
  
    blockdev_path = yield_blockdev_path("main", "10GiB", args.main_disk_size, zvol_path)

    possibly_partition_main_disk(blockdev_path)

    log.info("check if main zpool is imported...")
    if zpool_ensure_import_if_importable(vmname):
      log.info(f"zpool `{vmname}` is imported.")
    else:
      log.info("zpool is not importable.")
      main_partition_blockdev = f"/dev/disk/by-partlabel/{vmname}-main"
      log.info(f"does zfs blockdev `{main_partition_blockdev}` exist...")
      if not does_path_exist(main_partition_blockdev):
        error_message = f"zfs blockdev {main_partition_blockdev} does not exist but should exist at this point. this is likely a bug."
        log.error(error_message)
        raise BaseException(error_message)
      else:
        log.info(f"zfs blockdev `{main_partition_blockdev}` exists.")
      exec_or(f"zpool create {vmname} -R {vmroot} /dev/disk/by-partlabel/{vmname}-main -o autotrim=on -O acltype=posix -O atime=off -O canmount=off -O dnodesize=auto -O utf8only=on -O xattr=sa -O mountpoint=none", f"could not create zpool: {vmname}")
  
    # for main, we need this, but data wont have this, see below
    if not does_zfs_dataset_exist(f"{vmname}/fsroot"):
      log.info(f"creating zfs: {vmname}/fsroot")
      exec_or(f"zfs create {vmname}/fsroot -o mountpoint=legacy -o normalization=formD", f"could not create zfs dataset: {vmname}/fsroot")
    else:
      log.info(f"zfs {vmname}/fsroot already exists")



    mkdirs(vmroot, ".")


    if is_zfs_manual_mount(f"{vmname}/fsroot"):
      log.info(f"mount zfs '{vmname}/fsroot' manually...")
      returncode, formatted_output, formatted_response, formatted_error = exec(f"mount -t zfs {vmname}/fsroot /var/vmm/{vmname}")
      if 0 != returncode:
        if not yes(f"could not mount zfs dataset: `{vmname}/fsroot`. Error: `{formatted_error[0]}` Do you want to continue?"):
          exit()

    mkdirs(f"{vmroot}", ["boot", "root", "etc", "nix", "data", "home"])
    chmods_replace(f"{vmroot}", ["etc", "nix", "data", "home"], [755])
  
    log.info("checking boot partition")
  
    boot_partition = f"{partition_prefix}-boot"
    if not is_formatted(boot_partition):
      log.info(f"formatting '{boot_partition}'")
      exec_or(f"mkfs.fat -F 32 -n \"{vmname[0:6]}-boot\" {boot_partition}", f"could not format: {boot_partition}")
    else:
      log.warning(f"partition `{boot_partition}` is already formatted. You can set the flag `--reformat-boot-partition` to reformat it.")
    
    classic_mount_if_not_mounted(boot_partition, f"{vmroot}/boot", blockdev_path)
  
  
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
    data_pool = f"{vmname}-{data_tag}"
    zvol_path = f"{args.zvol_parent_path}/vm-{data_pool}"
    
    blockdev_path = yield_blockdev_path({data_tag}, "4GiB", args.data_disk_size, zvol_path)


    possibly_partition_data_disk(blockdev_path) 

    log.info(f"checking if zpool `{data_pool}` is not imported...")
    if zpool_ensure_import_if_importable(data_pool):
      log.info(f"zpool `{data_pool}` is imported.")
    else:
      log.info("zpool is not importable.")
      data_partition_blockdev = f"/dev/disk/by-partlabel/{data_pool}"
      log.info(f"does zfs blockdev `{data_partition_blockdev}` exist...")
      if not does_path_exist(data_partition_blockdev):
        error_message = f"zfs blockdev `{data_partition_blockdev}` does not exist but should exist at this point. this is likely a bug."
        log.error(error_message)
        raise BaseException(error_message)
      else:
        log.info(f"zfs blockdev `{data_partition_blockdev}` exists.")
      log.info(f"create zpool `{data_pool} `...")
      exec_or(f"zpool create {data_pool} -R /var/vmm/{data_pool} /dev/disk/by-partlabel/{data_pool} -o autotrim=on -O acltype=posix -O atime=off -O dnodesize=auto -O utf8only=on -O xattr=sa -O mountpoint=/{data_tag} -O com.sun:auto-snapshot=true", f"could not create zpool: {data_pool}")
      log.info(f"zpool `{data_pool}` created.")

  data_pool_location = f"{vmroot}/{data_tag}"
  mkdirs(f"{data_pool_location}", ["root", "home"])
  chmods_replace(f"{data_pool_location}", [".", "home"], [755])
  chmods_replace(f"{data_pool_location}", ["root"], [700])
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

  partition_prefix = f"/dev/disk/by-partlabel/{vmname}"

  #alexTODO: division needs to be implemented (see http://etzchaim.k44/FeuK44/nixk44/-/issues/2)
  division = ""
  if args.division != None:
    division = f"-{args.division}"

  if zpool_ensure_import_if_importable(vmname):
    log.info(f"zpool `{vmname}` is imported.")
  else:
    error_message = f"main zpool `{vmname}` is not importable."
    log.error(error_message)
    raise BaseException(error_message)
  mount_legacy_if_zfs_is_legacy_mount(f"{vmname}/fsroot", f"{vmroot}")

  data_pool = f"{vmname}-data"

  data_pool_location = f"{vmroot}/{data_tag}"
  log.info(f"checking if data dataset of `{data_pool}` already exists...")
  if does_zfs_dataset_exist(data_pool):
    mount_legacy_if_zfs_is_legacy_mount(f"{vmname}/data", f"{data_pool_location}")
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
  mkdirs(f"{data_pool_location}", ["root", "home"])
  classic_mount_if_not_mounted(boot_partition, f"{vmroot}/boot", f"{boot_partition}")
  bind_mount(f"{data_pool_location}/root", f"{vmroot}/root")
  bind_mount(f"{data_pool_location}/home", f"{vmroot}/home")
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
  blockdev = f"/dev/zvol/{args.zvol_parent_path}/"
  raise NotImplementedError

def install(args):
  guard_vm_running(vmname)
  if args.zvol_parent_path == None:
    log.error("ERROR: the following arguments are required: --zvol_parent_path")
    return
  log.info("start mounting...")
  mount(args)
  log.info("mounting finished. installing...")
  create_snapshot(vmname, "auto_snapshot_before_install")
  root = args.path
  vmorg = args.vmorg
  if root == None:
    root = f"{mount_parent}/{vmname}"
  returncode, install_output, install_result, install_error = exec_or(f"cd {K44_VMM_ZION_PATH}; echo $PATH; nixos-install --flake ./{vmorg}/hosts/{vmname}#{vmname} --root {root} --impure --no-root-passwd", "nixos-install failed. Maybe you need to `set NIXPATH=...`?")
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
  create_snapshot(vmname, "auto_snapshot_after_install")

def make_snapshot(args):
  create_snapshot(args.vmname, args.snapshot_name)

def create_snapshot(vmname, snapshot_name = ""):
  # TODO: I can't find this function. We must create some library we can include.
  ##  now = Get_timestamp_for_filenames()
  # hence I replaced it with:
  now = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
  if snapshot_name != "":
    snapshot_name = "_" + snapshot_name
  vm_data = f"vm-{vmname}-data"
  vm_vda = f"vm-{vmname}-vda"
  data_snapshot_name = f"{vm_data}@{now}{snapshot_name}"
  vda_snapshot_name = f"{vm_vda}@{now}{snapshot_name}"

  data_snapshot_path = os.path.join(args.zvol_parent_path, data_snapshot_name)
  vda_snapshot_path = os.path.join(args.zvol_parent_path, vda_snapshot_name)
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

def enter(args):
  guard_vm_running(vmname)
  if args.path != None:
    exec(f"nixos-enter --root {args.path}")
  else:
    exec(f"nixos-enter --root {vmroot}")

def setup_wireguard():
  data_pool_location = f"{vmroot}/{data_tag}"
  keys_path = os.path.join(data_pool_location, "keys")
  wireguard_path = os.path.join(keys_path, "wireguard")
  feu_wireguard_path =  os.path.join(wireguard_path, "feu")
  knet_wireguard_path =  os.path.join(wireguard_path, "knet")
  mkdirs("", [keys_path, wireguard_path, feu_wireguard_path, knet_wireguard_path])
  chmods_replace("", [keys_path], [555])
  chmods_replace("", [wireguard_path, feu_wireguard_path, knet_wireguard_path], [550])
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
  chmods_replace("", [keys_path], [555])
  chmods_replace("", [wireguard_path, feu_wireguard_path], [550])
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
enter_parser.set_defaults(func=enter)
kill_parser.set_defaults(func=kill)
setup_vm_parser.set_defaults(func=setup_vm)
remove_vm_parser.set_defaults(func=remove_vm)
make_snapshot_parser.set_defaults(func=make_snapshot)




args = parser.parse_args()
vmname = args.vmname
vmroot = f"{mount_parent}/{vmname}"
verbose = args.verbose
silent = args.silent
returncode, formatted_output, formatted_response, formatted_error = exec("whoami")
try:
  if formatted_output[0] != "root":
    error_message = "You must be root!"
    log.error(error_message)
    raise BaseException(error_message)
  args.func(args)
except BaseException as exception:
  # TODO: this also seems to be from apoeschl logging, and I have no idea what it does
  # so I commented out the following line:
  ## error_message = str(traceback.format_exc()) + "\n" + str(exception)
  # and replaced it with
  error_message = exception

  log.error(error_message)
log.info("vmm finished!")
# the sleep is necessary so the debug logger gets flushed properly at and of script
time.sleep(1)
