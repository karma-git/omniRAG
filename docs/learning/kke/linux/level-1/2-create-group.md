---
title: "2 - Create a group"
tags:
  - kodekloud-engineer-sysadmin
---

## Task

There are specific access levels for users defined by the xFusionCorp Industries system admin team. Rather than providing access levels to every individual user, the team has decided to create groups with required access levels and add users to that groups as needed. See the following requirements:

a. Create a group named nautilus_admin_users in all App servers in Stratos Datacenter.

b. Add the user mohammed to nautilus_admin_users group in all App servers. (create the user if doesn't exist).

## Solution

```shell
thor@jump_host ~$ ssh tony@stapp01
[tony@stapp01 ~]$ sudo -i

[root@stapp01 ~]# cat /etc/passwd | grep mohammed
[root@stapp01 ~]# cat /etc/group | grep nautilus_admin_users

[root@stapp01 ~]# groupadd nautilus_admin_users
[root@stapp01 ~]# useradd -G nautilus_admin_users mohammed
[root@stapp01 ~]# cat /etc/passwd | grep mohammed
mohammed:x:1002:1004::/home/mohammed:/bin/bash
[root@stapp01 ~]# cat /etc/group | grep mohammed
nautilus_admin_users:x:1003:mohammed
```
