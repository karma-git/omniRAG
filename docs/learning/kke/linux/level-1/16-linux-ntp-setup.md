---
title: "16 - Linux NTP Setup"
tags:
  - kodekloud-engineer-sysadmin
---

## Task

The system admin team of xFusionCorp Industries has noticed an issue with some servers in Stratos Datacenter where some of the servers are not in sync w.r.t time. Because of this, several application functionalities have been impacted. To fix this issue the team has started using common/standard NTP servers. They are finished with most of the servers except App Server 1. Therefore, perform the following tasks on this server:

Install and configure NTP server on App Server 1.

Add NTP server 2.north-america.pool.ntp.org in NTP configuration on App Server 1.

Please do not try to start/restart/stop ntp service, as we already have a restart for this service scheduled for tonight and we don't want these changes to be applied right now.

## Solution

```shell
thor@jump_host ~$ ssh tony@stapp01
[tony@stapp01 ~]$ sudo -i
[root@stapp01 ~]# yum install ntp -y
# add server to list
[root@stapp01 ~]# vi /etc/ntp.conf
# check result
[root@stapp01 ~]# grep -E "^server [0-9]" /etc/ntp.conf
server 0.centos.pool.ntp.org iburst
server 1.centos.pool.ntp.org iburst
server 2.centos.pool.ntp.org iburst
server 3.centos.pool.ntp.org iburst
server 2.north-america.pool.ntp.org
```
