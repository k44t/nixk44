

{pkgs, lib, python3, python312Packages, bash, ...}@args:

pkgs.writeScriptBin "start-kmonad" ''
  #!${bash}/bin/bash
  ${python3.withPackages (pythonPackages: with pythonPackages; [
    python312Packages.videocr
  ])}/bin/python ${./videocr.py}
''