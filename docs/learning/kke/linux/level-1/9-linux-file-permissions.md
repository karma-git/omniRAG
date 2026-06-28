---
title: "9 - Linux File Permissions"
tags:
  - kodekloud-engineer-sysadmin
---

## Solution

```shell
# login to the target server
thor@jump_host ~$ ssh banner@stapp0

[banner@stapp03 ~]$ ls -la /tmp/xfusioncorp.sh
---------- 1 root root 40 Feb 10 08:46 /tmp/xfusioncorp.sh
[banner@stapp03 ~]$ sudo chmod +x /tmp/xfusioncorp.sh
[banner@stapp03 ~]$ sh /tmp/xfusioncorp.sh
sh: /tmp/xfusioncorp.sh: Permission denied
[banner@stapp03 ~]$ ls -la /tmp/xfusioncorp.sh
---x--x--x 1 root root 40 Feb 10 08:46 /tmp/xfusioncorp.sh
# w/o read permissions, script can not be executed

[banner@stapp03 ~]$ sudo chmod +rx /tmp/xfusioncorp.sh
[banner@stapp03 ~]$ ls -la /tmp/xfusioncorp.sh
-r-xr-xr-x 1 root root 40 Feb 10 08:46 /tmp/xfusioncorp.sh
[banner@stapp03 ~]$ sh /tmp/xfusioncorp.sh
Welcome To KodeKloud
# done
```
