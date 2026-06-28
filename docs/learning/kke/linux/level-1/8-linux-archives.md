---
title: "8 - Linux Archives"
tags:
  - kodekloud-engineer-sysadmin
---

## Task

On Nautilus storage server in Stratos DC, there is a storage location named /data, which is used by different developers to keep their data (non confidential data). One of the developers named ammar has raised a ticket and asked for a copy of their data present in /data/ammar directory on storage server. /home is a FTP location on storage server itself where developers can download their data. Below are the instructions shared by the system admin team to accomplish this task.



a. Make a ammar.tar.gz compressed archive of /data/ammar directory and move the archive to /home directory on Storage Server


## Solution

```shell
thor@jump_host ~$ ssh natasha@ststor01
[natasha@ststor01 ~]$ sudo -i
[root@ststor01 ~]# tar -zcvf ammar.tar.gz /data/ammar/
tar: Removing leading `/' from member names
/data/ammar/
/data/ammar/nautilus2.txt
/data/ammar/nautilus3.txt
/data/ammar/nautilus1.txt
[root@ststor01 ~]# mv ammar.tar.gz /home/
```
