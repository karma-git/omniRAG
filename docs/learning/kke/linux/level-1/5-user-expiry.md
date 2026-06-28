---
title: "5 - Linux User Expiry"
tags:
  - kodekloud-engineer-sysadmin
---

## Task

A developer james has been assigned Nautilus project temporarily as a backup resource. As a temporary resource for this project, we need a temporary user for james. It’s a good idea to create a user with a set expiration date so that the user won't be able to access servers beyond that point.
Therefore, create a user named james on the App Server 1. Set expiry date to 2021-01-28 in Stratos Datacenter. Make sure the user is created as per standard and is in lowercase.

## Solution

```shell
thor@jump_host ~$ ssh tony@stapp01
[tony@stapp01 ~]$ sudo -i
# add user with ttl
[root@stapp01 ~]# useradd --expiredate 2021-01-28 james
# make sure it has been created
[root@stapp01 ~]# ls /home/
ansible  james  tony
```
