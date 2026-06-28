---
title: "10 - Linux Collaborative Directories"
tags:
  - kodekloud-engineer-sysadmin
---

## Task

The Nautilus team doesn't want its data to be accessed by any of the other groups/teams due to security reasons and want their data to be strictly accessed by the sysadmin group of the team.

Setup a collaborative directory /sysadmin/data on Nautilus App 1 server in Stratos Datacenter.

The directory should be group owned by the group sysadmin and the group should own the files inside the directory. The directory should be read/write/execute to the group owners, and others should not have any access.

## Solution

```shell
[root@stapp01 ~]# mkdir -p /sysadmin/data
[root@stapp01 ~]# chown -R root:sysadmin /sysadmin/
[root@stapp01 ~]# chmod 770 -R /sysadmin/
[root@stapp01 ~]# ls -la /sysadmin/
total 12
drwxrwx--- 3 root sysadmin 4096 Feb 24 07:11 .
drwxr-xr-x 1 root root     4096 Feb 24 07:11 ..
drwxrwx--- 2 root sysadmin 4096 Feb 24 07:11 data
```