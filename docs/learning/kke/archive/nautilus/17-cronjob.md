---
title: "17 -cronjob"
tags:
  - kodekloud-engineer-sysadmin
---

## Task

The Nautilus system admins team has prepared scripts to automate several day-to-day tasks. They want them to be deployed on all app servers in Stratos DC on a set schedule. Before that they need to test similar functionality with a sample cron job. Therefore, perform the steps below:

a. Install cronie package on all Nautilus app servers and start crond service.

b. Add a cron */5 * * * * echo hello > /tmp/cron_text for root user.

## Solution

```shell
thor@jump_host ~$ ssh tony@stapp01
[tony@stapp01 ~]$ sudo -i
[root@stapp01 ~]# yum install -y cronie

# checking cron daemon
[root@stapp01 ~]# systemctl status crond
● crond.service - Command Scheduler
   Loaded: loaded (/usr/lib/systemd/system/crond.service; enabled; vendor preset: enabled)
   Active: inactive (dead)

Jul 13 03:56:40 stapp01.stratos.xfusioncorp.com systemd[1]: Collecting crond.service
Jul 13 03:56:40 stapp01.stratos.xfusioncorp.com systemd[1]: Trying to enqueue job crond.service/try-restart/replace
Jul 13 03:56:40 stapp01.stratos.xfusioncorp.com systemd[1]: Installed new job crond.service/nop as 98
Jul 13 03:56:40 stapp01.stratos.xfusioncorp.com systemd[1]: Enqueued job crond.service/nop as 98
Jul 13 03:56:40 stapp01.stratos.xfusioncorp.com systemd[1]: Job crond.service/nop finished, result=done
[root@stapp01 ~]# systemctl start crond
[root@stapp01 ~]# systemctl status crond
● crond.service - Command Scheduler
   Loaded: loaded (/usr/lib/systemd/system/crond.service; enabled; vendor preset: enabled)
   Active: active (running) since Thu 2023-07-13 03:57:50 UTC; 3s ago
 Main PID: 669 (crond)
   CGroup: /docker/6e63727b9c13df56299042aa1ed366e8477ce64ec39e70de0e8ccf919abaddb7/system.slice/crond.service
           └─669 /usr/sbin/crond -n

Jul 13 03:57:50 stapp01.stratos.xfusioncorp.com systemd[1]: About to execute: /usr/sbin/crond -n $CRONDARGS
Jul 13 03:57:50 stapp01.stratos.xfusioncorp.com systemd[1]: Forked /usr/sbin/crond as 669
Jul 13 03:57:50 stapp01.stratos.xfusioncorp.com systemd[1]: crond.service changed dead -> running
Jul 13 03:57:50 stapp01.stratos.xfusioncorp.com systemd[1]: Job crond.service/start finished, result=done
Jul 13 03:57:50 stapp01.stratos.xfusioncorp.com crond[669]: (CRON) INFO (Syslog will be used instead of sendmail.)
Jul 13 03:57:50 stapp01.stratos.xfusioncorp.com systemd[1]: Started Command Scheduler.
Jul 13 03:57:50 stapp01.stratos.xfusioncorp.com crond[669]: (CRON) INFO (RANDOM_DELAY will be scaled with factor 38% if used.)
Jul 13 03:57:50 stapp01.stratos.xfusioncorp.com crond[669]: (CRON) INFO (running with inotify support)
Jul 13 03:57:50 stapp01.stratos.xfusioncorp.com systemd[669]: Executing: /usr/sbin/crond -n

# add the string */5 * * * * echo hello > /tmp/cron_text into cron via editor
[root@stapp01 ~]# crontab -e
no crontab for root - using an empty one
crontab: installing new crontab
[root@stapp01 ~]# crontab -l
 */5 * * * * echo hello > /tmp/cron_text
```
