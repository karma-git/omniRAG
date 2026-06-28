---
title: "5 - Linux User Files"
tags:
  - kodekloud-engineer-sysadmin
---

## Task

There was some users data copied on Nautilus App Server 1 at /home/usersdata location by the Nautilus production support team in Stratos DC. Later they found that they mistakenly mixed up different user data there. Now they want to filter out some user data and copy it to another location. Find the details below:

On App Server 1 find all files (not directories) owned by user jim inside /home/usersdata directory and copy them all while keeping the folder structure (preserve the directories path) to /official directory.

## Try


```shell
# find files
[root@stapp01 ~]# ls -la /home/usersdata | grep jim
-rw-r--r--  1 jim  root   420 Feb 13 06:36 index.php
-rw-r--r--  1 jim  root  6939 Feb 13 06:36 wp-activate.php
-rw-r--r--  1 jim  root   369 Feb 13 06:36 wp-blog-header.php
-rw-r--r--  1 jim  root  2283 Feb 13 06:36 wp-comments-post.php
-rw-r--r--  1 jim  root  2898 Feb 13 06:36 wp-config-sample.php
-rw-r--r--  1 jim  root  3955 Feb 13 06:36 wp-cron.php
-rw-r--r--  1 jim  root  2504 Feb 13 06:36 wp-links-opml.php
-rw-r--r--  1 jim  root  3326 Feb 13 06:36 wp-load.php
-rw-r--r--  1 jim  root 47597 Feb 13 06:36 wp-login.php
-rw-r--r--  1 jim  root  8483 Feb 13 06:36 wp-mail.php
-rw-r--r--  1 jim  root 19120 Feb 13 06:36 wp-settings.php
-rw-r--r--  1 jim  root 31112 Feb 13 06:36 wp-signup.php
-rw-r--r--  1 jim  root  4764 Feb 13 06:36 wp-trackback.php
-rw-r--r--  1 jim  root  3150 Feb 13 06:36 xmlrpc.php
# copy files
[root@stapp01 ~]# for f in $(ls -la /home/usersdata | grep jim | awk '{print $9}'); do echo $f; cp /home/usersdata/$f /official; done
index.php
wp-activate.php
wp-blog-header.php
wp-comments-post.php
wp-config-sample.php
wp-cron.php
wp-links-opml.php
wp-load.php
wp-login.php
wp-mail.php
wp-settings.php
wp-signup.php
wp-trackback.php
xmlrpc.php
# check
[root@stapp01 ~]# ls /official/
index.php           wp-comments-post.php  wp-links-opml.php  wp-mail.php      wp-trackback.php
wp-activate.php     wp-config-sample.php  wp-load.php        wp-settings.php  xmlrpc.php
wp-blog-header.php  wp-cron.php           wp-login.php       wp-signup.php
# return ownership
[root@stapp01 ~]# chown -R jim:root /official
```

## Solution

```shell
[root@stapp02 ~]# ls -la /home/usersdata | grep siva
-rw-r--r--  1 siva root   420 Feb 13 06:53 index.php
-rw-r--r--  1 siva root  6939 Feb 13 06:53 wp-activate.php
-rw-r--r--  1 siva root   369 Feb 13 06:53 wp-blog-header.php
-rw-r--r--  1 siva root  2283 Feb 13 06:53 wp-comments-post.php
-rw-r--r--  1 siva root  2898 Feb 13 06:53 wp-config-sample.php
-rw-r--r--  1 siva root  3955 Feb 13 06:53 wp-cron.php
-rw-r--r--  1 siva root  2504 Feb 13 06:53 wp-links-opml.php
-rw-r--r--  1 siva root  3326 Feb 13 06:53 wp-load.php
-rw-r--r--  1 siva root 47597 Feb 13 06:53 wp-login.php
-rw-r--r--  1 siva root  8483 Feb 13 06:53 wp-mail.php
-rw-r--r--  1 siva root 19120 Feb 13 06:53 wp-settings.php
-rw-r--r--  1 siva root 31112 Feb 13 06:53 wp-signup.php
-rw-r--r--  1 siva root  4764 Feb 13 06:53 wp-trackback.php
-rw-r--r--  1 siva root  3150 Feb 13 06:53 xmlrpc.php
# cpio --pass-through --make-directories --preserve-modification-time
[root@stapp02 ~]# sudo find /home/usersdata -user siva -type f | cpio -pdm /ecommerce
67805 blocks
[root@stapp02 ~]# ls -la /ecommerce
total 12
drwxrwxrwx 3 root root 4096 Feb 13 06:57 .
drwxr-xr-x 1 root root 4096 Feb 13 06:53 ..
drwxr-xr-x 3 root root 4096 Feb 13 06:57 home
```
