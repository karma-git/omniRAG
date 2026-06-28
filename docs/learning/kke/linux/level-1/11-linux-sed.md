---
id: 11-linux-sed
title: "11 - Linux String Substitute"
tags:
  - kodekloud-engineer-sysadmin
---

## Task

The backup server in the Stratos DC contains several template XML files used by the Nautilus application. However, these template XML files must be populated with valid data before they can be used. One of the daily tasks of a system admin working in the xFusionCorp industries is to apply string and file manipulation commands!

Replace all occurances of the string Sample to Cloud on the XML file /root/nautilus.xml located in the backup server.

## Solution

```shell
[root@stbkp01 ~]# cat /root/nautilus.xml | grep Sample | uniq
      <genre>Sample</genre>

[root@stbkp01 ~]# sed -i "s/Sample/Cloud/g" /root/nautilus.xml
[root@stbkp01 ~]# cat /root/nautilus.xml | grep Sample | uniq
[root@stbkp01 ~]# cat /root/nautilus.xml | grep Cloud | uniq
      <genre>Cloud</genre>
```
