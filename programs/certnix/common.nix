{ config, lib, pkgs, ... }:
with lib; with types;
let 

in
{
  options = {
    country = mkOption {
      type = anything;
      default = {};
      defaultText = literalExpression "null";
      example = literalExpression ''DE'';
      description = ''
        Countrycode (2 characters)
      '';
    };

    state = mkOption {
      type = anything;
      default = {};
      defaultText = literalExpression "null";
      example = literalExpression ''Kentucky'';
      description = ''
        State
      '';
    };

    locality = mkOption {
      type = anything;
      default = {};
      defaultText = literalExpression "null";
      example = literalExpression ''New York City'';
      description = ''
        eg. City
      '';
    };

    organisation = mkOption {
      type = anything;
      default = {};
      defaultText = literalExpression "null";
      example = literalExpression ''K44'';
      description = ''
        eg. Company
      '';
    };

    organisational-unit = mkOption {
      type = anything;
      default = {};
      defaultText = literalExpression "null";
      example = literalExpression ''K44Cert'';
      description = ''
        eg. Company Department
      '';
    };

    # not inheritable
    common-name = mkOption {
      type = nullOr str;
      default = null;
      defaultText = literalExpression "null";
      example = literalExpression ''somename'';
      description = ''
        eg. name of certificate
      '';
    };
    email = mkOption {
      type = anything;
      default = {};
      defaultText = literalExpression "null";
      example = literalExpression ''somename'';
      description = ''
        eg. email of user
      '';
    };
    
    path-len = mkOption {
      type = anything;
      default = {};
    };
    
    valid-for = mkOption {
      type = anything;
      default = {};
      defaultText = literalExpression "356";
      example = literalExpression ''356'';
      description = ''
        the validity period of the certificate in days
      '';
    };
    
    hash = mkOption {
      type = anything;
      default = {};
    };
    
    # not inheritable!
    pfx = mkOption {
      type = bool;
      default = false;
    };
    
    subject-alt-name = mkOption {
      type = nullOr str;
      default = null;
      description = ''
        Among other uses this field allows to specify an email address to be used as a local-id for ikev2 (ipsec) vpn. For the email `name@example.com` its value would be `email:name@example.com`
      '';
    };
    
    encryption = mkOption {
      type = anything;
      default = {};
      defaultText = literalExpression "aes256";
      example = literalExpression ''aes256'';
      description = ''
        the encryption algorythm of the
      '';
    };
    
    
    bits = mkOption {
      type = anything;
      default = {};
    };
    
    
    self-sign = mkOption {
      type = anything;
      default = {};
      description = ''
        whether this should be self-signed
      '';
    };
  };
}