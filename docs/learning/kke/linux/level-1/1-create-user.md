---
title: "1 - Create a user"
tags:
  - kodekloud-engineer-sysadmin
---

## Task

For security reasons the xFusionCorp Industries security team has decided to use custom Apache users for each web application hosted, rather than its default user. This will be the Apache user, so it shouldn't use the default home directory. Create the user as per requirements given below:

a. Create a user named siva on the App server 1 in Stratos Datacenter.

b. Set its UID to 1709 and home directory to /var/www/siva.


## Solution

```shell
thor@jump_host ~$ ssh tony@stapp01
[tony@stapp01 ~]$ sudo -i
[root@stapp01 ~]# useradd --help
[root@stapp01 ~]# useradd --uid 1709 --home-dir /var/www/siva siva
```
