---
id: 6-linux-sed
title: "6 - Linux String Substitute (sed)"
tags:
  - kodekloud-engineer-sysadmin
---

## Task

There is some data on Nautilus App Server 1 in Stratos DC. Data needs to be altered in several of the files. On Nautilus App Server 1, alter the /home/BSD.txt file as per details given below:

a. Delete all lines containing word software and save results in /home/BSD_DELETE.txt file. (Please be aware of case sensitivity)

b. Replace all occurrence of word and to them and save results in /home/BSD_REPLACE.txt file.

Note: Let's say you are asked to replace word to with from. In that case, make sure not to alter any words containing this string; for example upto, contributor etc.

## Solution

```shell
[root@stapp01 ~]# cat /home/BSD.txt
Copyright (c) <year>, <copyright holder>
All rights reserved.
#...
# a
[root@stapp01 ~]# cp /home/BSD.txt /home/BSD_DELETE.txt
[root@stapp01 ~]# sed -i '/software/d' /home/BSD_DELETE.txt
[root@stapp01 ~]# cat /home/BSD_DELETE.txt | grep software
[root@stapp01 ~]# cp /home/BSD.txt /home/BSD_REPLACE.txt
# b
[root@stapp01 ~]# grep and /home/BSD_REPLACE.txt
Redistribution and use in source and binary forms, with or without
# ...
[root@stapp01 ~]# sed -i 's/and/them/g' /home/BSD_REPLACE.txt
[root@stapp01 ~]# grep and /home/BSD_REPLACE.txt
[root@stapp01 ~]# grep them /home/BSD_REPLACE.txt
Redistribution them use in source them binary forms, with or without
# ...
```
