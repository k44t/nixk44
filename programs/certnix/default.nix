{pkgs, lib, config, ...}@args:
let
  cfg = config.programs.certnix;
in  
with lib; with types; # use the functions from lib, such as mkIf
let
  hashrow-message = msg: ''
    echo 
    echo "########################################################"
    echo "${msg}"
    echo "########################################################"
    echo 
  '';
  
  defaultEncryption = "aes256";
  
  certnix = pkgs.stdenv.mkDerivation {
    name = "certnix";
    version = "custom";
    src = script;
    installPhase = ''
      mkdir -p $out/bin/
      cp -av $src/bin/certnix $out/bin/certnix
    '';
    dontUnpack = true;
    # dontBuild = true;
    # dontStrip = true;
  };
  deps = with pkgs; [
    openssl 
    coreutils 
    findutils 
    gnugrep 
    rsync
    gnused
  ];
  path = concatStringsSep ":" (map mkPath deps);
  mkPath = pkg: concatStringsSep "/" [(toString pkg) "bin"];
  
  script = pkgs.writeScriptBin "certnix" ''
    #!/bin/sh
    if [[ "$2" == "--debug" ]] ; then
      set -x
    fi
    # exit on any error
    set -e
    
    export PATH=${path}
    ${import <nixk44/scripts/file_ending.nix}
    
    home="${cfg.home}"
    
    function askYesNo {
      QUESTION=$1
      DEFAULT=$2
      if [ "$DEFAULT" = true ]; then
              OPTIONS="[Y/n]"
              DEFAULT="y"
          else
              OPTIONS="[y/N]"
              DEFAULT="n"
      fi
      read -p "$QUESTION $OPTIONS " -n 1 -s -r INPUT
      INPUT=''${INPUT:-''${DEFAULT}}
      echo ''${INPUT}
      if [[ "$INPUT" =~ ^[yY]$ ]]; then
          ANSWER=true
      else
          ANSWER=false
      fi
    }

    function handleError {
      if [ "$1" == "" ]; then
        echo error: see above
      else
        echo error: $1
      fi
      read -p "press enter to continue..." INPUT
    }

    # askYesNo "Do it?" true
    # DOIT=$ANSWER
    
    if [[ "$1" == "build" ]] ; then
      ${optionalString (cfg.create-home) ''mkdir -p $home/private/''}
      cd $home/private/
      
      ${mkLocal cfg}
      
      cd ..; pwd
      echo "copying public files..."
      rsync -av ./private/ ./public/ --filter='+ *.cert.pem' --filter='+ *.cert.pfx' --filter='+ *.crl.pem' --filter="-! */" --prune-empty-dirs --delete
      
      ${hashrow-message "exiting successfully"}
    elif [[ "$1" == "info" ]] ; then
      if [[ "$2" == "public" ]] ; then
        ${pkgs.tree}/bin/tree --prune -F $home/public/;
      else
        ${pkgs.tree}/bin/tree --prune -F $home/private/;
      fi
    elif [[ "$1" == "change-passphrase" ]] ; then
      file=$2
      if [[ "$(file_ending "$2")" == "pem" ]]; then
        enc=$3
        enc=$(
          if [[ "$enc" != "" ]]; then
            echo "$enc"
          else
            echo ${defaultEncryption}
          fi
        )
        openssl rsa -$enc -in $file -out $file
      else
        echo "I have no idea how to change the passphrase of this filetype"
        exit 1
      fi
    elif [[ "$1" == "remove-passphrase" ]] ; then
      file=$2
      if [[ "$(file_ending "$2")" == "pem" ]]; then
        openssl rsa -in $file -out $file
      else
        echo "I have no idea how to remove the passphrase of this filetype"
        exit 1
      fi
    elif [[ "$1" == "view" ]] ; then
      file=$2
      if [[ "$(file_ending "$2")" == "pem" ]]; then
        openssl x509 -in $file -noout -text
      else
        echo "I have no idea how to open this filetype"
        exit 1
      fi
    else
      echo 'usage `certnix build|info|view|change-passphrase|remove-passphrase` (`--debug`)'
    fi
  '';
  
  strip = filterAttrs (n: v: v != {});
  
  
  mkPrivateKey = name: encryption: bits: ''
    if [[ ! -f ${name}.key.pem ]] ; then 
      echo generating private key '${name}.key.pem'
      openssl genrsa ${optionalString (encryption != null) "-${encryption}"} -out ${name}.key.pem ${toString bits} || handleError
      chmod 400 ${name}.key.pem
    fi
  '';
  
  mkServiceExtensionsHeader = {name, keyUsage ? "serverAuth"}: ''
    [ ${name} ]
    
      basicConstraints = critical, CA:FALSE
      subjectKeyIdentifier = hash
      authorityKeyIdentifier = keyid:always, issuer:always
      keyUsage = critical, nonRepudiation, digitalSignature, keyEncipherment, keyAgreement
      
      nsCertType = server
      nsComment = "OpenSSL Generated Server Certificate"
  '';
  
  mkClientExtensionsHeader = {name, keyUsage ? "serverAuth"}: ''
    [ ${name} ]
    
      basicConstraints = critical, CA:FALSE
      subjectKeyIdentifier = hash
      authorityKeyIdentifier = keyid:always, issuer:always
      keyUsage = critical, nonRepudiation, digitalSignature, keyEncipherment
      
      nsCertType = client, email
      nsComment = "OpenSSL Generated Client Certificate"
  '';
  
  mkLocal = {
    valid-for ? 365,
    hash ? "sha512",
    bits ? 4096,
    country,
    state,
    locality,
    organisation,
    organisational-unit ? null,
    common-name,
    pfx,
    encryption ? defaultEncryption,
    ...
  }@args: let
  
  in ''
    if [[ ! -d authorities ]] ; then mkdir authorities; fi
    cd authorities; pwd
      ${concatStringsSep "\n" (map (mkLocalAuthority args) (attrNames args.authorities))}
    cd ..; pwd
    
    
    if [[ ! -d services ]] ; then mkdir services; fi
    cd services; pwd
      ${hashrow-message "managing local services"}
      ${concatStringsSep "\n" (map (mkLocalService args) (attrNames args.services))}
    cd ..; pwd
    if [[ ! -d clients ]] ; then mkdir clients; fi
    cd clients; pwd
      ${hashrow-message "managing local clients"}
      ${concatStringsSep "\n" (map (mkLocalClient args) (attrNames args.clients))}
    cd ..; pwd;
  '';
  
  
  mkLocalAuthority = {
    ...
  }@args: name: let 
    authority = args.authorities.${name};
  in mkAuthority (
    (strip args) // {
      name = name; 
      authority = authority;
    } // (strip cfg) // (strip authority)
  );
  
  mkLocalService = {
    is-sub ? false,
    local ? true,
    self-sign ? false,
    ...
  }@args: name: let
    service = args.services.${name};
  in mkService ((strip args) // {
    name = name;
    service = service;
    is-sub = is-sub;
    local = local;
    self-sign = self-sign;
  } // (strip service));

  mkLocalClient = {
    is-sub ? false,
    local ? true,
    self-sign ? false,
    ...
  }@args: name: let
    client = args.clients.${name};
  in mkClient ((strip args) // {
    name = name;
    client = client;
    is-sub = is-sub;
    local = local;
    self-sign = self-sign;
  } // (strip client));
  
  
  mkSan = ips: dns: let
    mkIp = ip: "IP:${ip}";
    mkDns = dns: "DNS:${dns}";
  in ''${concatStringsSep ", " (concatLists [(map mkDns dns) (map mkIp ips)])}'';
  
  
  mkService = args: mkServiceOrClient "service" mkClientExtensionsHeader ({extended-key-usage = "critical, serverAuth"; } // (strip args));
  
  mkServiceOrClient = type: ext-header-fn: {
    is-sub ? false,
    self-sign ? false,
    name,
    encryption ? defaultEncryption,
    local ? false,
    hash ? "sha512",
    bits ? 4096,
    pfx ? false,
    email ? null,
    extended-key-usage,
    ips ? [],
    dns ? [],
    subject-alt-name ? null,
    ...
  }@conf: let
    
    req-conf = pkgs.writeText "${name}.req.openssl.conf" ''
      ${mkReqConfHeader "my_extensions" conf}

      ${ext-header-fn {name = "my_extensions";}}
        ${ext}
    '';
    ext = ''
        extendedKeyUsage = ${extended-key-usage}
        ${
          let 
            v = concatStringsSep ", " (filter (v: v != "") [
              (optionalString (type == "service") (mkSan ips dns))
              (optionalString (subject-alt-name != null) subject-alt-name)
            ]);
          in optionalString (v != "") "subjectAltName = ${v}"
        }
    '';
    ext-conf = pkgs.writeText "${name}.ext.openssl.conf" ext;
    
    genReq = ''openssl req -utf8  -config ./req.openssl.conf -new -key ./private/${name}.key.pem -out ./${name}.csr.pem || handleError'';
    
  in ''
    ${hashrow-message "managing ${type} '${name}'"}
    if [[ ! -d ${name} ]] ; then mkdir ${name}; fi
    cd ${name}; pwd
      if [[ ! -f ./${name}.cert.pem ]] ; then
        set -xe
        cp ${ext-conf} ./ext.openssl.conf
        ${optionalString local ''
          if [[ ! -d private ]] ; then mkdir private; fi
          cd private; pwd
            ${mkPrivateKey name encryption bits}
          cd ..; pwd
          cp ${req-conf} ./req.openssl.conf
          ${optionalString (is-sub && !self-sign) genReq}
          ${optionalString (!is-sub && self-sign) ''
            openssl req -utf8 -key ./private/${name}.key.pem -config ./req.openssl.conf -new -x509 -out ./${name}.cert.pem || handleError
          ''}
        ''}
        ${optionalString is-sub (mkSuperSign "${type}s" "ext.openssl.conf" conf)}
      fi
      ${optionalString pfx (mkPfx name local)}
    cd ..; pwd
    ${hashrow-message "finished managing ${type} '${name}'"}
  '';
  
  mkClient = {
    name,
    email ? null,
    common-name ? null,
    ...
  }@args: 
    mkServiceOrClient "client" mkClientExtensionsHeader ({
      extended-key-usage = "critical, clientAuth, emailProtection"; 
      #email = if (common-name == null && email != null) then email else name; 
    } // (strip args));
  
  mkPfx = name: with-private-key: ''
    ${optionalString with-private-key ''
      if [[ ! -f ./private/${name}.key.pfx ]] ; then
        echo exporting keypair `pwd`/private/${name}.key.pfx
        openssl pkcs12 -export -inkey ./private/${name}.key.pem -in ./${name}.cert.pem -name "${name}" -out ./private/${name}.key.pfx || handleError
      fi
    ''}
    if [[ ! -f ./${name}.cert.pfx ]] ; then
      echo exporting certificate `pwd`/${name}.cert.pfx
      openssl pkcs12 -passout pass:admin -nokeys -export -in ./${name}.cert.pem -name "${name}" -out ./${name}.cert.pfx || handleError
    fi
  '';
  
  mkSuperSign = type: ext-file: {
    name,
    valid-for ? 365,
    ...
  }: ''
    if [[ ! -f ${name}.cert.pem ]] ; then
      echo "signing CSR by '${name}'"
      cd ../..; pwd
      openssl ca -utf8 -batch -config ./conf/${type}.openssl.conf -notext -days ${toString valid-for} -in ./${type}/${name}/${name}.csr.pem ${optionalString (ext-file != null) ''-extfile ${if hasPrefix "/" "${ext-file}" then "${ext-file}" else "./${type}/${name}/${ext-file}"}''} -out ./${type}/${name}/${name}.cert.pem || handleError
      cd ${type}/${name}; pwd
    fi
  '';
  
  mkReqConfHeader = x509-section: {
    hash ? "sha512",
    bits ? 4096,
    country,
    state,
    locality,
    organisation,
    organisational-unit ? null,
    common-name ? null,
    email ? null,
    dn-section ? "my_dn",
    ...
  }@conf: ''
      [ req ]
    
        prompt = no

        string_mask         = utf8only

        default_bits        = ${toString bits}

        # SHA-1 is deprecated, so use SHA-2 instead.
        default_md          = ${hash}

        distinguished_name  = ${dn-section}
        
        x509_extensions     = ${x509-section}
      
      [ ${dn-section} ]
        
        C  = ${country}
        ST = ${state}
        L  = ${locality}
        O  = ${organisation}
        ${optionalString (organisational-unit != null) "OU = ${organisational-unit}"}
        ${optionalString (common-name != null) "CN = ${common-name}"}
        ${optionalString (email != null) "emailAddress = ${email}"}
  '';
  
  mkRevoke = authority: name: let 
    rev = authority.revoked."${name}";
    serial = if (isInt rev.serial) 
      then lib.toHexString rev.serial
      else rev.serial;
  in ''
    # echo "managing revocation of '${name}' (${serial})"
    revoked=$( grep -E '^R\s\w+\s\w+\s${serial}\b' data/index.db || true )
    # echo grepped
    if [[ $revoked == "" ]]; then
      echo "revoking certificate '${name}' (${serial})"
      openssl ca -config ./conf/self.openssl.conf -revoke ${optionalString (rev.reason != null) "-crl_reason ${rev.reason}"} ./certs/${serial}.pem || handleError
    else
      echo "already revoked: '${name}' (${serial})"
    fi
    # echo revocation done
  '';
  
  mkAuthority = {
    is-sub ? false,
    authority,
    path-len ? 0,
    name,
    self-sign ? false,
    valid-for ? 365,
    hash ? "sha512",
    bits ? 4096,
    country,
    state,
    locality,
    organisation,
    organisational-unit ? null,
    common-name,
    pfx,
    encryption ? defaultEncryption,
    crl-uris ? [],
    ...
  }@args: let
  
    mkSubAuthority = name: let
      sub = authority.authorities.${name};
    in mkAuthority (args // {
      is-sub = true;
      authority = sub;
      revoke = [];
      name = name;
      self-sign = false;
      crl-uris = [];
      path-len = if path-len == 0 then 0 else path-len - 1;
    } // (strip sub));
  
    mkSubService = name: let
      service = authority.services.${name};
    in mkService ((strip args) // (strip service) // {
      is-sub = true;
      name = name;
      service = service;
    });
  
    mkSubClient = name: let
      client = authority.clients.${name};
    in mkClient ((strip args) // (strip client) // {
      is-sub = true;
      name = name;
      client = client;
    });
  
  
    self-conf = pkgs.writeText "${name}.self.openssl.conf" ''
      ${common-ca-conf}
      
        default_days      = ${toString valid-for}

      ${mkReqConfHeader "my_extensions" args}
      
      [ my_extensions ]
        
        subjectKeyIdentifier = hash
        authorityKeyIdentifier = keyid:always,issuer:always
        basicConstraints = critical, CA:true ${optionalString (path-len >= 0) '', pathlen:${toString path-len}''}
        keyUsage = critical, digitalSignature, cRLSign, keyCertSign
    '';
    
    crl-conf = pkgs.writeText "${name}.crl.openssl.conf" ''
      ${common-ca-conf}

        crlnumber         = $dir/data/crl-number.txt
        crl               = $dir/${name}.crl.pem
        
        default_crl_days  = 30

        crl_extensions = my_extensions
      
      [ my_extensions ]
        
        authorityKeyIdentifier = keyid:always,issuer:always
    '';
    
    common-ca-conf = ''
      [ ca ]
        default_ca      = my_ca
      
      [ my_ca ]
      
        ${paths-conf}

        default_md        = ${hash}

        name_opt          = ca_default
        cert_opt          = ca_default
        
        preserve          = no
        
    '';
    
    paths-conf = ''
      dir               = .
      certs             = $dir/certs
      new_certs_dir     = $dir/certs
      database          = $dir/data/index.db
      serial            = $dir/data/serial.txt
      RANDFILE          = $dir/private/random.txt
      private_key       = $dir/private/${name}.key.pem
      certificate       = $dir/${name}.cert.pem
    '';
    
    clients-conf = pkgs.writeText "${name}.clients.openssl.conf" ''
      ${common-ca-conf}
      
        default_days = 365
      
        policy = my_policy
      
        x509_extensions = my_extensions
      
      [ my_policy ]
      
        countryName             = match
        stateOrProvinceName     = match
        localityName            = match
        organizationName        = match
        organizationalUnitName  = optional
        commonName              = supplied
        emailAddress            = optional
      
      ${mkServiceExtensionsHeader {name = "my_extensions";}}
    '';
    
    services-conf = pkgs.writeText "${name}.services.openssl.conf" ''
      ${common-ca-conf}
      
        default_days = 365
      
        policy = my_policy
      
        x509_extensions = my_extensions
      
      [ my_policy ]
      
        countryName             = match
        stateOrProvinceName     = match
        localityName            = match
        organizationName        = match
        organizationalUnitName  = optional
        commonName              = supplied
        emailAddress            = optional
      
      ${mkServiceExtensionsHeader {name = "my_extensions";}}
      
    '';
    
    index-db-attr = pkgs.writeText "${name}.index.db.attr" ''
        # this allows us to regenerate certificates for servers which have expired
        unique_subject    = no
    '';
    authorities-conf = pkgs.writeText "${name}.authorities.openssl.conf" ''
      ${common-ca-conf}
      
        default_days = 365
      
        policy = my_policy
      
        x509_extensions = my_extensions
      
      [ my_policy ]
      
        countryName             = match
        stateOrProvinceName     = match
        localityName            = match
        organizationName        = match
        organizationalUnitName  = optional
        commonName              = supplied
        emailAddress            = optional
      
      [ my_extensions ]
        
        subjectKeyIdentifier = hash
        authorityKeyIdentifier = keyid:always, issuer:always
        basicConstraints = critical, CA:true ${optionalString (path-len >= 0) '', pathlen:${toString path-len}''}
        keyUsage = critical, digitalSignature, cRLSign, keyCertSign
        ${optionalString (crl-uris != []) ''crlDistributionPoints = URI:${concatStringsSep ", URI:" crl-uris}''}

    '';
  in ''
  
    ${hashrow-message "building authority '${name}'"}
    if [[ ! -d ${name} ]] ; then mkdir ${name}; fi
    cd ${name}; pwd
      if [[ ! -d data ]] ; then mkdir data; fi
      cd data; pwd
        if [[ ! -f serial.txt ]] ; then echo 1000 > serial.txt; fi
        if [[ ! -f crl-number.txt ]] ; then echo 1000 > crl-number.txt; fi
        if [[ ! -f index.db ]] ; then touch index.db; fi
        cp ${index-db-attr} ./index.db.attr
      cd ..; pwd
      if [[ ! -d crl ]] ; then mkdir crl; fi
      if [[ ! -d certs ]] ; then mkdir certs; fi
      if [[ ! -d private ]] ; then mkdir private; fi
      cd private; pwd
        ${mkPrivateKey name encryption bits}
      cd ..; pwd
      if [[ ! -d conf ]] ; then mkdir conf; fi
      cd conf
        cp ${self-conf} ./self.openssl.conf
        cp ${crl-conf} ./crl.openssl.conf
        cp ${authorities-conf} ./authorities.openssl.conf
        cp ${services-conf} ./services.openssl.conf
        cp ${clients-conf} ./clients.openssl.conf
       
      cd ..; pwd
      if [[ ! -f ${name}.cert.pem ]] ; then
        ${if (self-sign == true) then ''
          echo self-signing authority certificate
          openssl req -utf8 -key ./private/${name}.key.pem -config conf/self.openssl.conf -new -x509 -out ./${name}.cert.pem || handleError
          ${optionalString pfx (mkPfx name true)}
        '' else ''
          echo creating CSR for authority
          openssl req -utf8  -config ./conf/self.openssl.conf -new -key ./private/${name}.key.pem -out ./${name}.csr.pem || handleError
          ${optionalString (is-sub) ''
            ${mkSuperSign "authorities" null args}
          ''}
        ''}
      fi 
      ${optionalString pfx (mkPfx name true)}
      
      ${hashrow-message "revoking certificates"}
      
      
      ${concatStringsSep "\n" (map (mkRevoke authority) (attrNames authority.revoked))}
      
      ${hashrow-message "managing CRL of '${name}'"}
      
      askYesNo "Would you like to (re-) generate the CRL of '${name}'?" false
      if [ "$ANSWER" = true ]; then
        openssl ca -config ./conf/crl.openssl.conf -gencrl -out ./${name}.crl.pem || handleError
      fi
      
      if [[ ! -d authorities ]] ; then mkdir authorities; fi
      cd authorities; pwd
        ${hashrow-message "managing sub-authorities of '${name}'"}
        ${concatStringsSep "\n" (map (mkSubAuthority) (attrNames authority.authorities))}
      cd ..; pwd
      if [[ ! -d services ]] ; then mkdir services; fi
      cd services; pwd
        ${hashrow-message "managing services of '${name}'"}
        ${concatStringsSep "\n" (map (mkSubService) (attrNames authority.services))}
      cd ..; pwd
      if [[ ! -d clients ]] ; then mkdir clients; fi
      cd clients; pwd
        ${hashrow-message "managing clients of '${name}'"}
        ${concatStringsSep "\n" (map (mkSubClient) (attrNames authority.clients))}
      cd ..; pwd
      ${hashrow-message "finished building authority '${name}'"}
    cd ..; pwd
  '';
  
  
  
  
in
{

  options = {
    programs = {
      certnix = lib.mkOption {
        type = submodule (import ./certnix.nix);
      };
    };
  };
  config = {
    programs.certnix.package = certnix;
  };
}
