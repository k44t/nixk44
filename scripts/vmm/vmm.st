# @@@@@@@@@@@@@@@@@@@@@@@@@@@
  example structure for vmm
  @@@@@@@@@@@@@@@@@@@@@@@@@@@

# this is the vm host's zpool. eva is also the name of the vm host.
zpool: eva
  zfs dataset | filesystem : fsroot
    
    # this is eva's root directory
    #mountpoint: /

  zfs dataset | filesystem : vms

    # this is the main disk for the vm `banah`
      blockdev: `/dev/zvol/eva/vms/vm-banah-vda`
    zfs dataset | volume: vm-banah-vda
      partition table

        # `/dev/disk/by-partlabel/banah-boot`
        partition: banah-boot
          
          # must be mounted at `/boot` of banah
          vfat filesystem

        
        
        # `/dev/disk/by-partlabel/banah-main`
        partition: banah-main
          zpool: banah
            dataset | filesystem: fsroot

              # mountpoint is relative to banah's root `/`
              #mountpoint: `/`

              # this is either a normal directory, or the zfs dataset (filesystem) `banah/etc` will be mounted here (overshadow this directory)
              directory: etc

              # this will be the `pointer` of a bind-mount which will be `pointing` to banah's `/data/home`
              directory: home

              directory: data

              # this will be the `pointer` of a bind-mount which will be `pointing` to banah's `/data/root`
              directory: root

              # here the boot partition must be mounted
              directory: boot


              


            # optional
            dataset | filesystem: etc

              # this mount will overshadow directory named `etc` in dataset (filesystem) `fsroot`
              #mountpoint: `/etc`


            # optional
            dataset | filesystem: nix


            # optional
              
              if this dataset exists, then zpool `banah-data` is not allowed to exist!
            dataset | filesystem: data

              # mountpoint is relative to banah's root `/`
              #mountpoint: /data



  
    # this is the data disk for the vm `banah`
      `/dev/zvol/eva/vms/vm-banah-data`
    zfs dataset | volume: vm-banah-data
      partition table
        partition: banah-data

          # if this zpool exists, then the zfs dataset (filesytem) `bana/data` is not allowed to exist!
          zpool: banah-data
            # this is the automatically created "root" dataset of the banah-data zpool (every zpool has a corresponding zfs dataset that cannot be deleted and is named just like the pool)
            dataset | filesystem: bana-data

              # mountpoint is relative to banah's root `/`
              #mountpoint: /data
              # and since the zfs property `mountpoint` is *not* set to `legacy` this will automatically be mounted once the zpool `bana-data` is imported

              directory: root
              directory: home