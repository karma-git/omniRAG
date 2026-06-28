---
title: "14 - MariaDB Troubleshooting"
tags:
  - kodekloud-engineer-sysadmin
---

## Task

There is a critical issue going on with the Nautilus application in Stratos DC. The production support team identified that the application is unable to connect to the database. After digging into the issue, the team found that mariadb service is down on the database server.

Look into the issue and fix the same.

## Solution

```shell
thor@jump_host ~$ ssh peter@stdb01
[peter@stdb01 ~]$ sudo -i
[root@stdb01 ~]# systemctl status mariadb
● mariadb.service - MariaDB database server
   Loaded: loaded (/usr/lib/systemd/system/mariadb.service; disabled; vendor preset: disabled)
   Active: inactive (dead)

Mar 04 08:38:08 stdb01.stratos.xfusioncorp.com systemd[1]: Collecting mariadb.service
[root@stdb01 ~]# systemctl start mariadb
Job for mariadb.service failed because the control process exited with error code. See "systemctl status mariadb.service" and "journalctl -xe" for details.
[root@stdb01 ~]# systemctl status mariadb.service
● mariadb.service - MariaDB database server
   Loaded: loaded (/usr/lib/systemd/system/mariadb.service; disabled; vendor preset: disabled)
   Active: failed (Result: exit-code) since Sat 2023-03-04 08:38:24 UTC; 8s ago
  Process: 644 ExecStartPost=/usr/libexec/mariadb-wait-ready $MAINPID (code=exited, status=1/FAILURE)
  Process: 643 ExecStart=/usr/bin/mysqld_safe --basedir=/usr (code=exited, status=0/SUCCESS)
  Process: 562 ExecStartPre=/usr/libexec/mariadb-prepare-db-dir %n (code=exited, status=0/SUCCESS)
 Main PID: 643 (code=exited, status=0/SUCCESS)

Mar 04 08:38:24 stdb01.stratos.xfusioncorp.com systemd[1]: mariadb.service: main process exited, code=exited, status=0/SUCCESS
Mar 04 08:38:24 stdb01.stratos.xfusioncorp.com systemd[1]: Child 644 belongs to mariadb.service
Mar 04 08:38:24 stdb01.stratos.xfusioncorp.com systemd[1]: mariadb.service: control process exited, code=exited status=1
Mar 04 08:38:24 stdb01.stratos.xfusioncorp.com systemd[1]: mariadb.service got final SIGCHLD for state start-post
Mar 04 08:38:24 stdb01.stratos.xfusioncorp.com systemd[1]: mariadb.service changed start-post -> failed
Mar 04 08:38:24 stdb01.stratos.xfusioncorp.com systemd[1]: Job mariadb.service/start finished, result=failed
Mar 04 08:38:24 stdb01.stratos.xfusioncorp.com systemd[1]: Failed to start MariaDB database server.
Mar 04 08:38:24 stdb01.stratos.xfusioncorp.com systemd[1]: Unit mariadb.service entered failed state.
Mar 04 08:38:24 stdb01.stratos.xfusioncorp.com systemd[1]: mariadb.service failed.
Mar 04 08:38:24 stdb01.stratos.xfusioncorp.com systemd[1]: mariadb.service: cgroup is empty

# check log

[root@stdb01 ~]# cat /var/log/mariadb/mariadb.log
230304 08:38:23 mysqld_safe Starting mysqld daemon with databases from /var/lib/mysql
230304  8:38:23 [Note] /usr/libexec/mysqld (mysqld 5.5.68-MariaDB) starting as process 807 ...
230304  8:38:23 InnoDB: The InnoDB memory heap is disabled
230304  8:38:23 InnoDB: Mutexes and rw_locks use GCC atomic builtins
230304  8:38:23 InnoDB: Compressed tables use zlib 1.2.7
230304  8:38:23 InnoDB: Using Linux native AIO
230304  8:38:23 InnoDB: Initializing buffer pool, size = 128.0M
230304  8:38:23 InnoDB: Completed initialization of buffer pool
InnoDB: The first specified data file ./ibdata1 did not exist:
InnoDB: a new database to be created!
230304  8:38:23  InnoDB: Setting file ./ibdata1 size to 10 MB
InnoDB: Database physically writes the file full: wait...
230304  8:38:23  InnoDB: Log file ./ib_logfile0 did not exist: new to be created
InnoDB: Setting log file ./ib_logfile0 size to 5 MB
InnoDB: Database physically writes the file full: wait...
230304  8:38:23  InnoDB: Log file ./ib_logfile1 did not exist: new to be created
InnoDB: Setting log file ./ib_logfile1 size to 5 MB
InnoDB: Database physically writes the file full: wait...
InnoDB: Doublewrite buffer not found: creating new
InnoDB: Doublewrite buffer created
InnoDB: 127 rollback segment(s) active.
InnoDB: Creating foreign key constraint system tables
InnoDB: Foreign key constraint system tables created
230304  8:38:23  InnoDB: Waiting for the background threads to start
230304  8:38:24 Percona XtraDB (http://www.percona.com) 5.5.61-MariaDB-38.13 started; log sequence number 0
230304  8:38:24 [Note] Plugin 'FEEDBACK' is disabled.
230304  8:38:24 [Note] Server socket created on IP: '0.0.0.0'.
230304  8:38:24 [ERROR] mysqld: Can't create/write to file '/var/run/mariadb/mariadb.pid' (Errcode: 13)
230304  8:38:24 [ERROR] Can't start server: can't create PID file: Permission denied
230304 08:38:24 mysqld_safe mysqld from pid file /var/run/mariadb/mariadb.pid ended
'

[root@stdb01 ~]# sudo chown mysql:mysql /var/run/mariadb
[root@stdb01 ~]# systemctl start mariadb
[root@stdb01 ~]# systemctl status mariadb
● mariadb.service - MariaDB database server
   Loaded: loaded (/usr/lib/systemd/system/mariadb.service; disabled; vendor preset: disabled)
   Active: active (running) since Sat 2023-03-04 08:41:49 UTC; 5s ago
  Process: 906 ExecStartPost=/usr/libexec/mariadb-wait-ready $MAINPID (code=exited, status=0/SUCCESS)
  Process: 871 ExecStartPre=/usr/libexec/mariadb-prepare-db-dir %n (code=exited, status=0/SUCCESS)
 Main PID: 905 (mysqld_safe)
   CGroup: /docker/97137255199a76253e5deb28cdc42b8d169e9cc2f01f5060480288b7b787034c/system.slice/mariadb.service
           ├─ 905 /bin/sh /usr/bin/mysqld_safe --basedir=/usr
           └─1069 /usr/libexec/mysqld --basedir=/usr --datadir=/var/lib/mysql --plugin-dir=/usr/lib64/mysql/plugin --log-error=/var/log/mariadb/mariad...

Mar 04 08:41:47 stdb01.stratos.xfusioncorp.com systemd[906]: Executing: /usr/libexec/mariadb-wait-ready 905
Mar 04 08:41:47 stdb01.stratos.xfusioncorp.com systemd[905]: Executing: /usr/bin/mysqld_safe --basedir=/usr
Mar 04 08:41:47 stdb01.stratos.xfusioncorp.com mysqld_safe[905]: 230304 08:41:47 mysqld_safe Logging to '/var/log/mariadb/mariadb.log'.
Mar 04 08:41:47 stdb01.stratos.xfusioncorp.com mysqld_safe[905]: 230304 08:41:47 mysqld_safe Starting mysqld daemon with databases from /var/lib/mysql
Mar 04 08:41:49 stdb01.stratos.xfusioncorp.com systemd[1]: Child 906 belongs to mariadb.service
Mar 04 08:41:49 stdb01.stratos.xfusioncorp.com systemd[1]: mariadb.service: control process exited, code=exited status=0
Mar 04 08:41:49 stdb01.stratos.xfusioncorp.com systemd[1]: mariadb.service got final SIGCHLD for state start-post
Mar 04 08:41:49 stdb01.stratos.xfusioncorp.com systemd[1]: mariadb.service changed start-post -> running
Mar 04 08:41:49 stdb01.stratos.xfusioncorp.com systemd[1]: Job mariadb.service/start finished, result=done
Mar 04 08:41:49 stdb01.stratos.xfusioncorp.com systemd[1]: Started MariaDB database server.
```
