---
title: "18 - Linux Banner"
tags:
  - kodekloud-engineer-sysadmin
---

## Task

During the monthly compliance meeting, it was pointed out that several servers in the Stratos DC do not have a valid banner. The security team has provided serveral approved templates which should be applied to the servers to maintain compliance. These will be displayed to the user upon a successful login.

Update the message of the day on all application and db servers for Nautilus. Make use of the approved template located at /home/thor/nautilus_banner on jump host

## Solution

```shell
thor@jump_host ~$ scp /home/thor/nautilus_banner steve@stapp02:/tmp
thor@jump_host ~$ ssh steve@stapp02
[steve@stapp02 ~]$ sudo mv /tmp/nautilus_banner /etc/motd
```

db server
```shell
thor@jump_host ~$ scp /home/thor/nautilus_banner peter@stdb01:/tmp
peter@stdb01's password: 
bash: scp: command not found
lost connection

thor@jump_host ~$ ssh peter@stdb01
[root@stdb01 ~]# yum -y install openssh-clients
[root@stdb01 ~]# scp
usage: scp [-12346BCpqrv] [-c cipher] [-F ssh_config] [-i identity_file]
           [-l limit] [-o ssh_option] [-P port] [-S program]
           [[user@]host1:]file1 ... [[user@]host2:]file2

thor@jump_host ~$ scp /home/thor/nautilus_banner peter@stdb01:/tmp
thor@jump_host ~$ ssh peter@stdb01
[peter@stdb01 ~]$ sudo mv /tmp/nautilus_banner /etc/motd
```
