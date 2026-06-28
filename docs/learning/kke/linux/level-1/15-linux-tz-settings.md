---
title: "15 - Linux TimeZones Setting"
tags:
  - kodekloud-engineer-sysadmin
---

## Solution

```shell
thor@jump_host ~$ ssh tony@stapp01
[tony@stapp01 ~]$ sudo -i
# check current tz
[root@stapp01 ~]# timedatectl; date +%z; date +%Z
# create symlink
[root@stapp01 ~]# ln -sf /usr/share/zoneinfo/Asia/Kabul /etc/localtime
# check time again
[root@stapp01 ~]# timedatectl
```
