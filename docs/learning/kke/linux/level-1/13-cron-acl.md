---
title: "13 - Cron schedule deny to users"
tags:
  - kodekloud-engineer-sysadmin
---

## Task


To stick with the security compliances, the Nautilus project team has decided to apply some restrictions on crontab access so that only allowed users can create/update the cron jobs. Limit crontab access to below specified users on App Server 3.

Allow crontab access to anita user and deny the same to eric user.

## Solution

```shell
thor@jump_host ~$ ssh banner@stapp03
[banner@stapp03 ~]$ sudo -i
[root@stapp03 ~]# echo "anita" > /etc/cron.allow
[root@stapp03 ~]# echo "eric" > /etc/cron.deny
# checking
[root@stapp03 cron.d]# su anita
[anita@stapp03 cron.d]$ crontab -l
no crontab for anita
[anita@stapp03 cron.d]$ exit
exit
[root@stapp03 cron.d]# su eric
[eric@stapp03 cron.d]$ crontab -l
You (eric) are not allowed to use this program (crontab)
See crontab(1) for more information
```
