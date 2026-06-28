---
title: "10 - Linux Access Control List"
tags:
  - kodekloud-engineer-sysadmin
---

## Task

The Nautilus security team performed an audit on all servers present in Stratos DC. During the audit some critical data/files were identified which were having the wrong permissions as per security standards. Once the report was shared with the production support team, they started fixing the issues. It has been identified that one of the files named /etc/hostname on Nautilus App 3 server has wrong permissions, so that needs to be fixed and the correct ACLs needs to be set.



1. The user owner and group owner of the file should be root user.

2. Others must have read only permissions on the file.

3. User anita must not have any permission on the file.

4. User garrett should have read only permission on the file.

## Solution

### first try

```shell
thor@jump_host ~$ ssh banner@stapp03
[banner@stapp03 ~]$ sudo -i
[root@stapp03 ~]# ls -la /etc/hostname 
-rw-r--r-- 1 root root 32 Jul 29 08:23 /etc/hostname

[root@stapp03 ~]# setfacl -m u:anita:-,u:garrett:r /etc/hostname 
[root@stapp03 ~]# ls -la /etc/hostname 
-rw-r--r--+ 1 root root 32 Jul 29 08:23 /etc/hostname

[root@stapp03 ~]# getfacl /etc/hostname 
getfacl: Removing leading '/' from absolute path names
# file: etc/hostname
# owner: root
# group: root
user::rw-
user:anita:---
user:garrett:r--
group::r--
mask::r--
other::r--

[root@stapp03 ~]# su anita
[anita@stapp03 root]$ cat /etc/hostname 
cat: /etc/hostname: Permission denied

[anita@stapp03 root]$ exit
exit
[root@stapp03 ~]# su garrett
[garrett@stapp03 root]$ cat /etc/hostname 
stapp03.stratos.xfusioncorp.com
```
