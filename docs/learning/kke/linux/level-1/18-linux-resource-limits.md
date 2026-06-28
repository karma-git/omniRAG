---
title: "18 - Linux Resource Limits"
tags:
  - kodekloud-engineer-sysadmin
---

## Task

On our Storage server in Stratos Datacenter we are having some issues where nfsuser user is holding hundred of processes, which is degrading the performance of the server. Therefore, we have a requirement to limit its maximum processes. Please set its maximum process limits as below:

a. soft limit = 1025

b. hard_limit = 2025


## Solution

```shell
[root@ststor01 ~]# ulimit --help
[root@ststor01 ~]# echo "nfsuser soft nproc 1025" >> /etc/security/limits.conf
[root@ststor01 ~]# echo "nfsuser hard nproc 2025" >> /etc/security/limits.conf
# NOTE: have noidea why limits doesn't show to the user
[root@ststor01 ~]# ulimit -a nfsuser
core file size          (blocks, -c) 0
data seg size           (kbytes, -d) unlimited
scheduling priority             (-e) 0
file size               (blocks, -f) unlimited
pending signals                 (-i) 837932
max locked memory       (kbytes, -l) 65536
max memory size         (kbytes, -m) unlimited
open files                      (-n) 1024
pipe size            (512 bytes, -p) 8
POSIX message queues     (bytes, -q) 819200
real-time priority              (-r) 0
stack size              (kbytes, -s) 8192
cpu time               (seconds, -t) unlimited
max user processes              (-u) unlimited
virtual memory          (kbytes, -v) unlimited
file locks                      (-x) unlimited
[root@ststor01 ~]# cat  /etc/security/limits.conf
...
```
