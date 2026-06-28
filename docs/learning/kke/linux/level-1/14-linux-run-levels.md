---
title: "14 - Linux Run Setup"
tags:
  - kodekloud-engineer-sysadmin
---

## Task

New tools have been installed on the app server in Stratos Datacenter. Some of these tools can only be managed from the graphical user interface. Therefore, there are requirements for these app servers.

On all App servers in Stratos Datacenter change the default runlevel so that they can boot in GUI (graphical user interface) by default. Please do not try to reboot these servers

## Solution

```shell
thor@jump_host ~$ ssh tony@stapp01
[tony@stapp01 ~]$ sudo -i
[root@stapp01 ~]# systemctl get-default
multi-user.target
[root@stapp01 ~]# systemctl set-default graphical.target
Removed symlink /etc/systemd/system/default.target.
Created symlink from /etc/systemd/system/default.target to /usr/lib/systemd/system/graphical.target.
[root@stapp01 ~]# systemctl status graphical.traget
Unit graphical.traget.service could not be found.
[root@stapp01 ~]# systemctl start graphical.target
[root@stapp01 ~]# systemctl status graphical.target
● graphical.target - Graphical Interface
   Loaded: loaded (/usr/lib/systemd/system/graphical.target; enabled; vendor preset: disabled)
   Active: active since Wed 2023-03-01 09:01:08 UTC; 9s ago
     Docs: man:systemd.special(7)

Mar 01 09:01:08 stapp01.stratos.xfusioncorp.com systemd[1]: Job graphical.target/start finished, result=done
Mar 01 09:01:08 stapp01.stratos.xfusioncorp.com systemd[1]: Reached target Graphical Interface.
[root@stapp01 ~]# systemctl get-default
graphical.target
```
