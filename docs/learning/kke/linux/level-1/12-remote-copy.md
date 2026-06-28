---
title: "12 - Linux Remote Copy"
tags:
  - kodekloud-engineer-sysadmin
---

## Task

One of the Nautilus developers has copied confidential data on the jump host in Stratos DC. That data must be copied to one of the app servers. Because developers do not have access to app servers, they asked the system admins team to accomplish the task for them.

Copy /tmp/nautilus.txt.gpg file from jump server to App Server 3 at location /home/code.


## Solution

```shell
thor@jump_host ~$ scp /tmp/nautilus.txt.gpg banner@stapp03:/home/code
nautilus.txt.gpg                                       100%  105   402.1KB/s   00:00
```
