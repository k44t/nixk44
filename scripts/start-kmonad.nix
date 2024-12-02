{pkgs, lib,  ...}@args:
pkgs.writeScriptBin "start-kmonad" ''
  #!${pkgs.bash}/bin/bash
  export PATH=${pkgs.envsubst}/bin:${pkgs.kmonad}/bin:${pkgs.list-input-devices}/bin:${pkgs.gnused}/bin:${pkgs.gnugrep}bin:$PATH
  dev_selector=$1
  conf=$2
  loglevel=$3
  echo device selector: $dev_selector
  echo configuration: $conf

  echo finding virtual device...
  export DEV=$(list-input-devices | grep -E "$dev_selector" | sed -E "s/:.+//g")

  if [ "$DEV" == "" ]; then echo virtual device not found; exit 1; fi

  echo device: "\"$DEV\""
  CFG=$(cat $conf | envsubst)
  # if [ "$3" == "debug" ];
  # then
  #  echo $CFG
  # fi
  echo entering kmonad process...
  if [ "$dloglevel" != "" ]; then
    kmonad --log-level $loglevel <(echo "$CFG") "''${@:3}"
  else
    kmonad <(echo "$CFG") "''${@:3}"
  fi
''
