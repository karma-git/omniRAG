---
title: "11 - Linux Postfix Troubleshooting"
tags:
  - kodekloud-engineer-sysadmin
---

## Task

Some users of the monitoring app have reported issues with xFusionCorp Industries mail server. They have a mail server in Stork DC where they are using postfix mail transfer agent. Postfix service seems to fail. Try to identify the root cause and fix it.

## Solution

```shell
thor@jump_host ~$ ssh groot@stmail01
[groot@stmail01 ~]$ sudo -i
[root@stmail01 ~]# systemctl status postfix -l
● postfix.service - Postfix Mail Transport Agent
   Loaded: loaded (/usr/lib/systemd/system/postfix.service; enabled; vendor preset: disabled)
   Active: failed (Result: exit-code) since Sun 2023-02-26 07:49:07 UTC; 20s ago
  Process: 636 ExecStart=/usr/sbin/postfix start (code=exited, status=1/FAILURE)
  Process: 635 ExecStartPre=/usr/libexec/postfix/chroot-update (code=exited, status=0/SUCCESS)
  Process: 632 ExecStartPre=/usr/libexec/postfix/aliasesdb (code=exited, status=75)

Feb 26 07:49:06 stmail01.stratos.xfusioncorp.com postfix[636]: fatal: parameter inet_interfaces: no local interface found for ::1
Feb 26 07:49:07 stmail01.stratos.xfusioncorp.com systemd[1]: Child 636 belongs to postfix.service
Feb 26 07:49:07 stmail01.stratos.xfusioncorp.com systemd[1]: postfix.service: control process exited, code=exited status=1
Feb 26 07:49:07 stmail01.stratos.xfusioncorp.com systemd[1]: postfix.service got final SIGCHLD for state start
Feb 26 07:49:07 stmail01.stratos.xfusioncorp.com systemd[1]: postfix.service changed start -> failed
Feb 26 07:49:07 stmail01.stratos.xfusioncorp.com systemd[1]: Job postfix.service/start finished, result=failed
Feb 26 07:49:07 stmail01.stratos.xfusioncorp.com systemd[1]: Failed to start Postfix Mail Transport Agent.
Feb 26 07:49:07 stmail01.stratos.xfusioncorp.com systemd[1]: Unit postfix.service entered failed state.
Feb 26 07:49:07 stmail01.stratos.xfusioncorp.com systemd[1]: postfix.service failed.
Feb 26 07:49:07 stmail01.stratos.xfusioncorp.com systemd[1]: postfix.service: cgroup is emp

```


```shell
thor@jump_host ~$ ssh groot@stmail01
[groot@stmail01 ~]$ sudo -i
# check systemd service
[root@stmail01 ~]# systemctl status postfix -l
● postfix.service - Postfix Mail Transport Agent
   Loaded: loaded (/usr/lib/systemd/system/postfix.service; enabled; vendor preset: disabled)
   Active: failed (Result: exit-code) since Sun 2023-02-26 07:49:07 UTC; 20s ago
  Process: 636 ExecStart=/usr/sbin/postfix start (code=exited, status=1/FAILURE)
  Process: 635 ExecStartPre=/usr/libexec/postfix/chroot-update (code=exited, status=0/SUCCESS)
  Process: 632 ExecStartPre=/usr/libexec/postfix/aliasesdb (code=exited, status=75)

Feb 26 07:49:06 stmail01.stratos.xfusioncorp.com postfix[636]: fatal: parameter inet_interfaces: no local interface found for ::1
Feb 26 07:49:07 stmail01.stratos.xfusioncorp.com systemd[1]: Child 636 belongs to postfix.service
Feb 26 07:49:07 stmail01.stratos.xfusioncorp.com systemd[1]: postfix.service: control process exited, code=exited status=1
Feb 26 07:49:07 stmail01.stratos.xfusioncorp.com systemd[1]: postfix.service got final SIGCHLD for state start
Feb 26 07:49:07 stmail01.stratos.xfusioncorp.com systemd[1]: postfix.service changed start -> failed
Feb 26 07:49:07 stmail01.stratos.xfusioncorp.com systemd[1]: Job postfix.service/start finished, result=failed
Feb 26 07:49:07 stmail01.stratos.xfusioncorp.com systemd[1]: Failed to start Postfix Mail Transport Agent.
Feb 26 07:49:07 stmail01.stratos.xfusioncorp.com systemd[1]: Unit postfix.service entered failed state.
Feb 26 07:49:07 stmail01.stratos.xfusioncorp.com systemd[1]: postfix.service failed.
Feb 26 07:49:07 stmail01.stratos.xfusioncorp.com systemd[1]: postfix.service: cgroup is empty

# stat string in interesting: <fatal: parameter inet_interfaces: no local interface found for ::1>

[root@stmail01 ~]# grep inet_interface /etc/postfix/main.cf
# The inet_interfaces parameter specifies the network interface
inet_interfaces = all
#inet_interfaces = $myhostname
#inet_interfaces = $myhostname, localhost
inet_interfaces = localhost
# the address list specified with the inet_interfaces parameter.
# receives mail on (see the inet_interfaces parameter).
# to $mydestination, $inet_interfaces or $proxy_interfaces.
# - destinations that match $inet_interfaces or $proxy_interfaces,
# unknown@[$inet_interfaces] or unknown@[$proxy_interfaces] is returned

# lets try to comment localhost as an interface for postfix

[root@stmail01 ~]# sed -i 's/inet_interfaces = localhost/#inet_interfaces = localhost/g' /etc/postfix/main.cf 
[root@stmail01 ~]# grep "inet_interface =" /etc/postfix/main.cf
inet_interfaces = all
#inet_interfaces = $myhostname
#inet_interfaces = $myhostname, localhost
#inet_interfaces = localhost

# let's start systemd service

[root@stmail01 ~]# systemctl start postfix
[root@stmail01 ~]# systemctl status postfix
● postfix.service - Postfix Mail Transport Agent
   Loaded: loaded (/usr/lib/systemd/system/postfix.service; enabled; vendor preset: disabled)
   Active: active (running) since Sun 2023-02-26 07:52:27 UTC; 4s ago
  Process: 665 ExecStart=/usr/sbin/postfix start (code=exited, status=0/SUCCESS)
  Process: 664 ExecStartPre=/usr/libexec/postfix/chroot-update (code=exited, status=0/SUCCESS)
  Process: 660 ExecStartPre=/usr/libexec/postfix/aliasesdb (code=exited, status=0/SUCCESS)
 Main PID: 736 (master)
   CGroup: /docker/728f7a365de3f10b391b861b430145697192dcfb68b6acd81bbb46d8f1f4f5f6/system.slice/postfix.service
           ├─736 /usr/libexec/postfix/master -w
           ├─737 pickup -l -t unix -u
           └─738 qmgr -l -t unix -u

Feb 26 07:52:27 stmail01.stratos.xfusioncorp.com systemd[665]: Executing: /usr/sbin/postfix start
Feb 26 07:52:27 stmail01.stratos.xfusioncorp.com postfix/master[736]: daemon started -- version 2.10.1, configuration /etc/postfix
Feb 26 07:52:27 stmail01.stratos.xfusioncorp.com systemd[1]: Child 665 belongs to postfix.service
Feb 26 07:52:27 stmail01.stratos.xfusioncorp.com systemd[1]: postfix.service: control process exited, code=exited status=0
Feb 26 07:52:27 stmail01.stratos.xfusioncorp.com systemd[1]: postfix.service got final SIGCHLD for state start
Feb 26 07:52:27 stmail01.stratos.xfusioncorp.com systemd[1]: New main PID 736 belongs to service, we are happy.
Feb 26 07:52:27 stmail01.stratos.xfusioncorp.com systemd[1]: Main PID loaded: 736
Feb 26 07:52:27 stmail01.stratos.xfusioncorp.com systemd[1]: postfix.service changed start -> running
Feb 26 07:52:27 stmail01.stratos.xfusioncorp.com systemd[1]: Job postfix.service/start finished, result=done
Feb 26 07:52:27 stmail01.stratos.xfusioncorp.com systemd[1]: Started Postfix Mail Transport Agent.
[root@stmail01 ~]#
```
