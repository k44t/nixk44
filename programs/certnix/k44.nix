{ config, lib, pkgs, ... }@args:
{
  country = "Germany";
  organization = "K44";
  ou = "IT";
  
  services = {
    "tyre-webserver" = {
      dns = ["*.tyre.k44", "tyre.k44"];
      ips = ["10.44.0.90"];
    };
  };

}