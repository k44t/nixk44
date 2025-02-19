{pkgs, lib,  ...}@args:
pkgs.writeScriptBin "start-kmonad" ''
  #!${pkgs.bash}/bin/bash
  export PATH=${pkgs.envsubst}/bin:${pkgs.kmonad}/bin:${pkgs.list-input-devices}/bin:${pkgs.gnused}/bin:${pkgs.gnugrep}bin:$PATH
  dev_regex=$1
  conf=$3


  export OUTDEV=$2

  echo device selector: $dev_regex
  echo configuration: $conf

  echo finding virtual device...
  export INDEV=$(list-input-devices | grep -E "$dev_regex" | sed -E "s/:.+//g")

  if [ "$INDEV" == "" ]; then echo virtual device not found; exit 1; fi

  echo device: "\"$INDEV\""
  echo output device: "\"$OUTDEV\""
  export DEV=$INDEV
  CFG=$(cat $conf | envsubst)
  echo entering kmonad process...
  kmonad <(echo "$CFG") "''${@:4}"
''
