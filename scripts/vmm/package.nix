{
  writeShellScriptBin
, callPackage
, zfs
, libvirt 
, coreutils
, gnugrep
, util-linux
, nixos-install
, nix
, mount
, nixos-install-tools
}: 
let
  path = builtins.concatStringsSep ":" (map (p: "${p}/bin") [
    zfs libvirt coreutils gnugrep util-linux nixos-install-tools nix mount
  ]);     

in
writeShellScriptBin "vmm" ''
  #!/usr/bin/env bash
  export PATH=${callPackage ./python.nix {}}/bin:${path}:$PATH
  python /#/zion/nixk44/scripts/vmm/vmm.py "$@"
  # python -Xfrozen_modules=off -m debugpy --wait-for-client --listen localhost:8888 /#/zion/nixk44/scripts/vmm/vmm.py "$@"
''

