---
title: "19 - Selinux Installation"
tags:
  - kodekloud-engineer-sysadmin
---

## Task

The xFusionCorp Industries security team recently did a security audit of their infrastructure and came up with ideas to improve the application and server security. They decided to use SElinux for an additional security layer. They are still planning how they will implement it; however, they have decided to start testing with app servers, so based on the recommendations they have the following requirements:

Install the required packages of SElinux on App server 3 in Stratos Datacenter and disable it permanently for now; it will be enabled after making some required configuration changes on this host. Don't worry about rebooting the server as there is already a reboot scheduled for tonight's maintenance window. Also ignore the status of SElinux command line right now; the final status after reboot should be disabled.

## Solution

```shell
[root@stapp03 ~]# yum install policycoreutils policycoreutils-python-utils selinux-policy selinux-policy-targeted libselinux-utils setroubleshoot-server setools setools-console mcstrans -y
[root@stapp03 ~]# sestatus
SELinux status:                 disabled
[root@stapp03 ~]# sed -i "s/SELINUX=enforcing/SELINUX=disabled/" /etc/selinux/config
[root@stapp03 ~]# grep SELINUX /etc/selinux/config
SELINUX=disabled
```
