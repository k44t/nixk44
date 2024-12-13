import re
import json
import os
import os.path

def myexec(command):
  return os.popen(command).read()
exec = myexec

def is_bind_mounted_as(pointed, pointing):
  pointers = exec(f"findmnt --noheadings --output source {pointing}")
  regexp_pattern = r'\[(.*)\]'
  regexp_searcher = re.compile(regexp_pattern)
  if type(pointers) != list:
    pointers = [pointers]
  for pointer in pointers:
    pointer = pointer.replace("\n", "")
    pointer_stripped = re.sub(regexp_pattern, '', pointer)
    mount_json_string = exec(f"findmnt --noheadings --output source,target {pointer_stripped} --json")
    mounts_json = json.loads(mount_json_string)
    for mount in mounts_json["filesystems"]:
      if "[" in mount["source"]:
        continue
      target_root = mount["target"]
      target_path = regexp_searcher.search(pointer).groups()[0]
      target = os.path.join(target_root, target_path)
      if target == pointed:
        return True
  return False

print(is_bind_mounted_as("/lib", "/var/temporarymount/"))