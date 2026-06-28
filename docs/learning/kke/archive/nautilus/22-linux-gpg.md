---
title: "22 - Linux GPG Encryption"
tags:
  - kodekloud-engineer-sysadmin
---

## Task

We have confidential data that needs to be transferred to a remote location, so we need to encrypt that data.We also need to decrypt data we received from a remote location in order to understand its content.



On storage server in Stratos Datacenter we have private and public keys stored /home/*_key.asc. Use those keys to perform the following actions.

Encrypt /home/encrypt_me.txt to /home/encrypted_me.asc.

Decrypt /home/decrypt_me.asc to /home/decrypted_me.txt. (Passphrase for decryption and encryption is kodekloud).


## Solution

```shell
thor@jump_host ~$ ssh natasha@ststor01
[natasha@ststor01 ~]$ sudo -i
[root@ststor01 ~]# cd /home/

[root@ststor01 home]# gpg --import private_key.asc --import public_key.asc
gpg: directory `/root/.gnupg' created
gpg: new configuration file `/root/.gnupg/gpg.conf' created
gpg: WARNING: options in `/root/.gnupg/gpg.conf' are not yet active during this run
gpg: keyring `/root/.gnupg/secring.gpg' created
gpg: keyring `/root/.gnupg/pubring.gpg' created
gpg: key CCE3AF51: secret key imported
gpg: /root/.gnupg/trustdb.gpg: trustdb created
gpg: key CCE3AF51: public key "kodekloud <kodekloud@kodekloud.com>" imported
gpg: can't open `--import': No such file or directory
gpg: key CCE3AF51: "kodekloud <kodekloud@kodekloud.com>" not changed
gpg: Total number processed: 2
gpg:               imported: 1  (RSA: 1)
gpg:              unchanged: 1
gpg:       secret keys read: 1
gpg:   secret keys imported: 1
'

[root@ststor01 home]# gpg --list-keys
/root/.gnupg/pubring.gpg
------------------------
pub   2048R/CCE3AF51 2020-01-19
uid                  kodekloud <kodekloud@kodekloud.com>
sub   2048R/865C070D 2020-01-19

[root@ststor01 home]# gpg --list-secret-key
/root/.gnupg/secring.gpg
------------------------
sec   2048R/CCE3AF51 2020-01-19
uid                  kodekloud <kodekloud@kodekloud.com>
ssb   2048R/865C070D 2020-01-19

[root@ststor01 home]# gpg --encrypt -r kodekloud@kodekloud.com --armor < encrypt_me.txt  -o encrypted_me.asc
gpg: 865C070D: There is no assurance this key belongs to the named user

pub  2048R/865C070D 2020-01-19 kodekloud <kodekloud@kodekloud.com>
 Primary key fingerprint: FEA8 5011 C456 B5E9 AE5A  516F 8F17 F26E CCE3 AF51
      Subkey fingerprint: 7B4B 5CFC 5E4F B4B6 EEC0  83E5 DD6B 8506 865C 070D

It is NOT certain that the key belongs to the person named
in the user ID.  If you *really* know what you are doing,
you may answer the next question with yes.

Use this key anyway? (y/N) y

# enter passphrase here
[root@ststor01 home]# gpg --decrypt decrypt_me.asc > decrypted_me.txt
gpg: AES encrypted data
gpg: encrypted with 1 passphrase

[root@ststor01 home]# cat decrypted_me.txt
Welcome to xFusionCorp Industries. This is KodeKloud System Administration Lab
[root@ststor01 home]# cat /home/encrypted_me.asc
-----BEGIN PGP MESSAGE-----
Version: GnuPG v2.0.22 (GNU/Linux)

hQEMA91rhQaGXAcNAQf+NS8QJIh9+aS9HEME+KP0P57k3+OHDnUqKJ+vKcHxfFLw
D4aoDsGTNXt3FIMwxknWM1fPBnPKQc9jtdHy2Ny/uDsmU24j8qEon0z2vMR99+04
NCZznsngczkpbhyw2wz3bkU5wzEd5EWjAjQsmtauRvj+eof+8+2BkIQr1PYxAnhL
25lFhqzYtbBTCquQdvu38KMZY7TeoWgv8HQq0aprLmYgGxz5fKoBTX+LNSujWb1b
hqkK1i8i/xcniguPkduYkLoRm51cqN+hpkrJ7O7KH4VlzTkxuoYZX/Ty5iipizCV
maxYSSZuvMKmxWCVj/sPElihVOSMdwTiwykB1EFZYdKUAcBZQYJNnmOD8Na5RL3k
i6mkwep1+zYBX4sP4GZACUfvkXRxy48cd89DjvEN2FemY+na1Y2dF0jA5fgHKWcH
IMVcSgDmH+wiWdPI9YLaH+CktR9ZNzfvD71aAGrTgK8c5efJq7L7O9vtQ0ZERUD6
fmqMR7VSAvg16jGPLJGVBC7cxtUoN82waF93FGg0BeW/p+b2Kg==
=r2sP
-----END PGP MESSAGE-----
```
