
{pkgs, ...}: let

vmm = pkgs.callPackage ./package.nix {};

in {
  environment.systemPackages = [ vmm ];

}




