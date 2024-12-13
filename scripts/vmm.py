import os, stat
import shutil
import re
import time
import subprocess
import json
from natsort import natsorted

import argparse


try:
  mount_parent = os.environ(['K44_VMM_MOUNT_ROOT'])
except Exception as e:
  print(f"ERROR: {e} - we will continue with `/var/vmm`")
  mount_parent = "/var/vmm"
try:
  K44_VMM_ZION_PATH = os.environ(['K44_VMM_ZION_PATH'])
except Exception as e:
  print(f"ERROR: {e} - we will continue with `/#/zion/k44`")
  K44_VMM_ZION_PATH = "/#/zion/k44"
try:
  K44_VMM_ZVOL_PARENT_PATH = os.environ(['K44_VMM_ZVOL_PARENT_PATH'])
except Exception as e:
  print(f"ERROR: {e} - we will continue with `None`")
  K44_VMM_ZVOL_PARENT_PATH = None

# Create the parser
parser = argparse.ArgumentParser(description="virtual machine worker")

subparser = parser.add_subparsers(required=True)

shared_parser = argparse.ArgumentParser(add_help=False)
shared_parser.add_argument("vmname", type=str, help="the name of the vm")

external_parser = argparse.ArgumentParser(add_help=False)
external_parser.add_argument("--path", type=str, help="path to where the nixos installation is mounted")

size_parser = argparse.ArgumentParser(add_help=False)
size_parser.add_argument("--data_disk_size", help="including a unit (10GiB, 1500M, ...)")
size_parser.add_argument("--main_disk_size", help="including a unit (10GiB), 1500M, ...)")

mountpoint_parser = argparse.ArgumentParser(add_help=False)
mountpoint_parser.add_argument("--aditional_binds", default=[], help="additional binds that should be mounted. Paths given are relative to the host's root. Example: /new/mountpoint:/existing/path,/new/mountpoint2:/existing/path2")

zvol_parser = argparse.ArgumentParser(add_help=False)
zvol_parser.add_argument("--zvol_parent_path", default=K44_VMM_ZVOL_PARENT_PATH, help="the zfs parent path under which to create the block devices")

# Add subparsers
create_parser = subparser.add_parser('create', parents=[shared_parser, zvol_parser, size_parser], help='checks if the virtual machine already exists, otherwise creates the virtual machine')
mount_parser = subparser.add_parser('mount', parents=[shared_parser, mountpoint_parser], help='mount an already existing virtual machine.')
unmount_parser = subparser.add_parser('unmount', parents=[shared_parser], help='unmount an already existing virtual machine.')
resize_parser = subparser.add_parser('resize', parents=[shared_parser, zvol_parser, size_parser], help='resize an already existing virtual machine.')
install_parser = subparser.add_parser('install', parents=[shared_parser, external_parser], help='install an already existing virtual machine.')
enter_parser = subparser.add_parser('enter', parents=[external_parser], help='enter an already existing virtual machine.')

#Add arguments fo subparsers
create_parser.add_argument("--data_disk_only", help="wether to ONLY create a data disk.")
create_parser.add_argument("--no_data_disk", help="wether to NOT create a data disk.")
create_parser.add_argument("--data_as_dataset", help="whether data is just a dataset and not a whole (possibly virtual) disk")
create_parser.add_argument("--force-partition-main-disk")
create_parser.add_argument("--force-partition-data-disk")
create_parser.add_argument("--force-format-boot-partition")

mount_parser.add_argument("--division", type=str, help="the suffix of a mirrored pool we are mounting (for a physical host)")

install_parser.add_argument("--vmorg", required=True, type=str, help="the organisation under which the vm shall be installed")

enter_parser.add_argument("vmname", type=str, help="the name of the vm")

def is_partitioned(blockdev):
  # -s means script
  # -q means that grep suppresses all output and only returns the exist status
  return exec_for_bool(f"parted -s {blockdev} print")

def exec_for_status(command):
  print(f"running command: `{command}`")
  result = subprocess.run(command, shell=True, capture_output=True)
  return result.returncode

# returns true if the command succe
def exec_for_bool(command):
  return exec_for_status(command) == 0

# we are overriding python's internal exec, which would execute python code dynamically, because we don't need nor like it
def myexec(command):
  print(f"running command: `{command}`")
  return os.popen(command).read()
exec = myexec

def mkdirs(root, dirs): 
  for d in dirs:
    new_directory_name = f"{root}/{d}"
    os.makedirs(new_directory_name, exist_ok=True)
    print(f"created directory: {new_directory_name}")

def is_zpool_imported(name):
  print(f"checking if pool `{name}` is already imported...")
  return exec_for_status(f"zpool list -H -o name | grep -q '^{name}$'") == 0
  
def is_zpool_importable(name):
  exec_for_status(f"zpool import | grep -q 'pool: {name}'") == 0

def yes(question):
  print(question + " (type yes):")
  is_sure = input()
  return is_sure == "yes"

def is_zfs_manual_mount(zfs_path):
  return exec(f"zfs get mountpoint {zfs_path} -H -o value") == "legacy"

def is_formatted(blockdev):
  return exec_for_status(f"blkid {blockdev} | grep -q 'TYPE='") == 0

def is_formatted_as(blockdev, filesystemtype):
  return exec_for_status(f"blkid {blockdev} | grep -q 'TYPE=\"{filesystemtype}\"'") == 0

def zfs_exists(zfs_path):
  return exec_for_bool(f"zfs list -H -o name | grep -q '{zfs_path}'")

def throw(message):
  raise ValueError(message)

def chmods(path, elements, rights):
  for element in elements:
    for right in rights:
      element_to_be_changed = f"{path}/{element}"
      os.chmod(element_to_be_changed, right)
      print(f"modify rights of '{element_to_be_changed}' to '{right}'")

def is_bind_mounted_as(pointed, pointing):
  print(pointing)
  pointers = exec(f"findmnt --noheadings --output source {pointing}")
  regexp_pattern = r'\[(.*)\]'
  regexp_searcher = re.compile(regexp_pattern)
  if type(pointers) != list:
    pointers = [pointers]
  print(pointers)
  for pointer in pointers:
    pointer = pointer.replace("\n", "")
    pointer_stripped = re.sub(regexp_pattern, '', pointer)
    mount_json_string = exec(f"findmnt --noheadings --output source,target {pointer_stripped} --json")
    mounts_json = json.loads(mount_json_string)
    for mount in mounts_json["filesystems"]:
      if "[" in mount["source"]:
        continue
      target_root = mount["target"]
      print(regexp_searcher)
      print(pointer)
      print(regexp_searcher.search(pointer))
      target_path = regexp_searcher.search(pointer).groups()[0]
      target = os.path.join(target_root, target_path)
      if target == pointed:
        return True
  return False

def bind_mount(pointing, pointed):
  if not is_bind_mounted_as(pointed, pointing):
    os.mkdirs(pointing, exist_ok=True)
    exec_or(f"mount --bind '{pointed}' '{pointed}'", f"bind mount failed from (pointing) '{pointing}' to (pointed) '{pointed}' path.")

def mount_additional_binds(list):
  for mnt in list.split(","):
    r = mnt.split(":")
    if len(r) != 2:
      throw(f"--additional-binds malformatted.")

def warn(msg):
  print(msg)

def exec_or(command, error_message):
  if not exec_for_bool(command):
    throw(error_message)

def exec_for_list(command):
  print(f"running command: `{command}`")
  return os.popen(command).readlines()
  
def import_zpool(poolname):
  exec_or(f"zpool import {poolname} -R {vmroot}", f"unable to import existing zpool {vmname}. Please destroy, make unavailable or import manually to proceed.")

def get_mountpoints(blockdev_or_zfs_path):
  return exec_for_list (f"findmnt --noheadings --output target {blockdev_or_zfs_path}")

def get_bind_mountpoints(pointer):
  return exec_for_list(f"findmnt --noheadings --output source {pointer}")

def is_mounted_as(blockdev, path):
  paths = get_mountpoints(blockdev)
  return path in paths

def is_mounted(blockdev):
  list = get_mountpoints(blockdev)
  return len(list) != 0

def create_blockdev(which, defaultsize, usersize, zvol_path):
  print(f"creating {which} disk: {zvol_path}")
  size = defaultsize
  if usersize != None:
    size = usersize
  exec_or(f"zfs create {zvol_path} -V {size}", f"could not create {which} disk: {zvol_path}")
  refresh_partitions()

def refresh_partitions():
  exec("udevadm trigger -v --subsystem-match=block '--sysname-match=zd*' --action=change")
  exec("udevadm settle")
  exec("partprobe")


def check_is_partitioned(blockdev, which, force):
  if is_partitioned(blockdev):
    if force:
      return True
    else:
      print(f"WARNING: {blockdev} is already partitioned. You can set the flag `--force-partition-{which}-disk` to repartition it.")

def partition_main_disk(blockdev):
  if check_is_partitioned(blockdev, "main", args.force_partition_main_disk):

    print(f"partitioning main disk: {blockdev}")
    error_message = f"could not format {blockdev}"
    exec_or(f"parted {blockdev} -- mklabel gpt", error_message)
    exec_or(f"parted {blockdev} -- mkpart {vmname}-boot 0% 1GiB", error_message)
    exec_or(f"parted {blockdev} -- set 1 boot on", error_message)
    exec_or(f"parted {blockdev} -- mkpart {vmname}-main 1GiB 100%", error_message)
    refresh_partitions()

def partition_data_disk(blockdev):
  if check_is_partitioned(blockdev, "data", args.force_partition_data_disk):

    print(f"partitioning data disk: {blockdev}")
    error_message = f"could not format {blockdev}"
    exec_or(f"parted {blockdev} -- mklabel gpt", error_message)
    exec_or(f"parted {blockdev} -- mkpart {vmname}-data 0% 100%", error_message)
    refresh_partitions()


def create(args):
    
    if args.zvol_parent_path == None:
      print("ERROR: the following arguments are required: --zvol_parent_path")
      return

    guard_vm_running(vmname)
    

    partition_prefix = f"/dev/disk/by-partlabel/{vmname}"
    
    vmroot = f"{mount_parent}/{vmname}"

    if not args.data_disk_only:
      # create main disk

        
    
      zvol_path = f"{args.zvol_parent_path}/vm-{vmname}-vda"
    
      if not zfs_exists(zvol_path):
        create_blockdev("main", "10GiB", args.main_disk_size, zvol_path)
      blockdev = f"/dev/zvol/{zvol_path}"
    
      if args.force_partition_main_disk:

      if is_zpool_imported(vmname):
        if args.force_partition_main_disk:
          print(f"zpool `export_zpool(vmname)
    
      if not is_zpool_imported(vmname):
        print(f"zpool `{vmname}` is not yet imported.")
        if is_zpool_importable(vmname):
          print(f"zpool `{vmname}` is importable. try to import zpool `{vmname}`...")
          import_zpool(vmname, f"")
          print(f"zpool `{vmname}` imported.")
        else:
          print(f"zpool `{vmname}` imported.")
          print(f"creating zpool: {vmname}")
          exec_or(f"zpool create {vmname} -R {vmroot} /dev/disk/by-partlabel/{vmname}-main -o autotrim=on -O acltype=posix -O atime=off -O canmount=off -O dnodesize=auto -O utf8only=on -O xattr=sa -O mountpoint=none", f"could not create zpool: {vmname}")
      else:
        print(f"zpool `{vmname}` is already imported.")
    
      if not zfs_exists(f"{vmname}/fsroot"):
        print(f"creating zfs: {vmname}/fsroot")
        exec_or(f"zfs create {vmname}/fsroot -o mountpoint=legacy -o normalization=formD", f"could not create zfs dataset: {vmname}/fsroot")
      else:
        print(f"zfs {vmname}/fsroot already exists")
      mkdirs(vmroot, ".")
    
      if is_zfs_manual_mount(f"{vmname}/fsroot"):
        print(f"mount zfs '{vmname}/fsroot' manually...")
        exec_or(f"mount -t zfs {vmname}/fsroot /mnt/{vmname}", f"could not mount zfs dataset: {vmname}/fsroot")
    
      mkdirs(f"{vmroot}", ["boot", "etc", "nix", "data", "root", "home"])
      chmods(f"{vmroot}", ["etc", "nix", "data", "home"], [stat.S_IREAD, stat.S_IEXEC])
    
    
      boot_partition = f"{partition_prefix}-boot"
      if not is_formatted(boot_partition) or args.reformat_boot_partition:
        print(f"formatting '{boot_partition}'")
        exec_or(f"mkfs.fat -F 32 -n \"{vmname[0:6]}-boot\" {boot_partition}", f"could not format: {boot_partition}")
      else:
        print(f"WARNING: partition `{boot_partition}` is already formatted. You can set the flag `--reformat-boot-partition` to reformat it.")
      
      
      if not is_mounted_as(boot_partition, f"{vmroot}/boot") and not exec_for_bool(f"mount /dev/disk/by-partlabel/{vmname}-boot boot"):
        exec_or(f"mount {boot_partition} {vmroot}/boot", f"failed to mount boot_partition: `{blockdev}`")
        print(f"mounted `{boot_partition} {vmroot}/boot`")
    
    
    create_data_disk = not args.no_data_disk
    
    if args.data_as_dataset:
      # create data as a dataset
      create_data_disk = False
      if not zfs_exists(f"{vmname}/data") and not exec_for_bool(f"zfs create {vmname}/data -o mountpoint=/data -o com.sun:auto-snapshot=true"):
        throw(f"failed to create zfs dataset: {vmname}/data")
    
    
    if create_data_disk:
      print("creating data disk (if necessary)")
      # create data disk
      blockdev = f"/dev/zvol/{args.zvol_parent_path}/{vmname}-data"

      data_pool = f"{vmname}-data"


      if is_zpool_imported(data_pool):
        print("data pool is already imported")

        

      # print("check if data zpool is imported...")
      if not is_zpool_imported(data_pool):
        print("data zpool is not imported.")
        print("checking if data zpool is importable...")
        if is_zpool_importable(data_pool):
          print("data zpool is importable, trying to import it...")
          import_zpool(data_pool)
          print("imported data zpool.")
        else:
          print("zpool is not importable.")
          print("does zfs blockdev exist?")
          if not zfs_exists(zvol_path):
            print("creating zfs blockdev for data-disk...")
            create_blockdev("data", "4GiB", args.main_disk_size, zvol_path)
            print("created blockdev for data.")
          print("checking if data is unpartitioned...")
          require_partition = False
          if is_partitioned(blockdev):
            if args.repartition_data_disk:
              print("overwriting data partition table is requested by the user...")
              require_partition = True
            else:
              warn(f"{blockdev} is already partitioned. You can set the flag `--repartition-data-disk` to repartition it.")
          else:
            print("partitioning is required.")
            require_partition = True
          if require_partition:        
           
            time.sleep(1)
            exec_or(f"zpool create {vmname}-data -R /mnt/{vmname} /dev/disk/by-partlabel/{vmname}-data -o autotrim=on -O acltype=posix -O atime=off -O dnodesize=auto -O utf8only=on -O xattr=sa -O mountpoint=/data -O com.sun:auto-snapshot=true"
              , error_message)
            print(f"created zpool for '{vmname}.")
            mkdirs(f"{vmroot}", ["root","home"])
            chmods(f"{vmroot}", [".", "home"], [stat.S_IREAD, stat.S_IEXEC])
          else:
            throw(f"failed to partition: {blockdev}")
    mkdirs(f"{vmroot}/data", ["root", "home"])
    chmods(f"{vmroot}/data", [".", "home"], [stat.S_IREAD, stat.S_IEXEC])
    bind_mount(f"{vmroot}/data/root", f"{vmroot}/root")
    bind_mount(f"{vmroot}/data/home", f"{vmroot}/home")
    mount_additional_binds(args.additional_binds)

def legacy_mount_zfs(zfs_path, fs_path, allow_failure=False):
  if not is_mounted_as(zfs_path, fs_path):
    if not exec_for_bool(f"mount -t zfs {zfs_path} {fs_path}") and not allow_failure:
        throw(f"failed to mount zfs: `{zfs_path}` @ `{fs_path}`")

def is_vm_running(vmname):
  # --name: return only the name
  # -q: no output, only exit code for success or failure
  return exec_for_bool(f"virsh list --name | grep -q '^{vmname}$'")

def guard_vm_running(vmname):
  vm_was_running = False
  if is_vm_running(vmname):
    vm_was_running = True
    if yes(f"VM `{vmname}` is currently up and running. Do you want to shut it down?"):
      exec(f"virsh shutdown {vmname}")
      time.sleep(10)
      if not is_vm_running(vmname):
        if yes(f"VM `{vmname}` is still running, do you want to kill it? (you can wait some more before you hit enter)"):
          exec(f"virsh destroy {vmname}")
        else:
          throw(f"exiting...")
      print(f"have shut down vm '{vmname}'")
    else:
      throw(f"exiting...")
  return vm_was_running

def mount(args):

  guard_vm_running(vmname)
  
  print(f"mounting host '{vmname}'...")

  vmroot = f"{mount_parent}/{vmname}"

  os.mkdir(f"{vmroot}")

  partition_prefix = "/dev/disk/by-partlabel/{vmname}"

  division = ""
  if args.division != None:
    division = f"-{args.division}"

  data_as_dataset = args.data_as_dataset

  exec_or(f"zpool import {vmname} -f -R {vmroot} -N", error_message=f"Could not mount main pool for '{vmname}'")

  legacy_mount_zfs(f"{vmname}/fsroot", f"{vmroot}", allow_failure=True)
  legacy_mount_zfs(f"{vmname}/etc", f"{vmroot}/etc", allow_failure=True)
  legacy_mount_zfs(f"{vmname}/nix", f"{vmroot}/nix", allow_failure=True)
  legacy_mount_zfs(f"{vmname}/data", f"{vmroot}/data", allow_failure=True)
  exec(f"zfs mount {vmname}/data")
  (f"zpool import {vmname}-data -f -R /mnt/{vmname}")
  legacy_mount_zfs(f"{vmname}-data", f"{vmroot}/data")
  mount_zfs(f"{vmname}/data")
  do_mount(f"{partition_prefixsion}-boot" f"{vmroot}/boot")
  
  bind(f"mount -o bind /mnt/{vmname}/data/home/ /mnt/{vmname}/home/")
  exec(f"mount -o bind /mnt/{vmname}/data/root/ /mnt/{vmname}/root/")
  mount_additional_binds(args.additional_binds)

def unmount(args):
  guard_vm_running(vmname)
  print(f"unmounting host '{vmname}'...")
  exec(f"umount -R /mnt/{vmname}")
  exec(f"zpool export {vmname}")
  exec(f"zpool export {vmname}-data")

def resize(args):
  guard_vm_running(vmname)
  blockdev = f"/dev/zvol/{args.zvol_parent_path}/"
  raise NotImplementedError

def install(args):
  guard_vm_running(vmname)
  root = args.path
  vmorg = args.vmorg
  if root == None:
    root = f"{mount_parent}/{vmname}"
  exec(f"nixos-install --flake {K44_VMM_ZION_PATH}/{vmorg}/hosts/{vmname}#{vmname} --root {root} --impure --no-root-passwd")

def enter(args):
  guard_vm_running(vmname)
  if args.path != None:
    exec(f"nixos-enter --root {args.path}")
  else:
    vmroot = f"{mount_parent}/{vmname}"
    exec(f"nixos-enter --root {vmroot}")

create_parser.set_defaults(func=create)
mount_parser.set_defaults(func=mount)
unmount_parser.set_defaults(func=unmount)
resize_parser.set_defaults(func=resize)
install_parser.set_defaults(func=install)
enter_parser.set_defaults(func=enter)
args = parser.parse_args()
vmname = args.vmname
args.func(args)

