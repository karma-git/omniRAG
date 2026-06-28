---
title: "7 - Linux Services"
tags:
  - kodekloud-engineer-sysadmin
---

## Task

As per details shared by the development team, the new application release has some dependencies on the back end. There are some packages/services that need to be installed on all app servers under Stratos Datacenter. As per requirements please perform the following steps:

- a. Install cups package on all the application servers.
- b. Once installed, make sure it is enabled to start during boot.

## Solution

```shell
[root@stapp01 ~]# yum install cups -y
[root@stapp01 ~]# systemctl start cups
[root@stapp01 ~]# systemctl enable cups
[root@stapp01 ~]# systemctl status cups
● cups.service - CUPS Printing Service
   Loaded: loaded (/usr/lib/systemd/system/cups.service; enabled; vendor preset: enabled)
   Active: active (running) since Sat 2023-02-18 14:28:19 UTC; 21s ago
 Main PID: 1319 (cupsd)
   CGroup: /docker/f6d71e8ebeeb7949671e89e458ed6acf9cebac2cd4b6e57ab0fb295b7db82953/system.slice/cups.service
           └─1319 /usr/sbin/cupsd -f

Feb 18 14:28:19 stapp01.stratos.xfusioncorp.com systemd[1]: Started CUPS Printing Service.
```
