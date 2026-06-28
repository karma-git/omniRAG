---
title: "shell / random Cheat Sheet"
tags:
  - bash
  - shell
  - linux
  - cheatsheet
---

## wget - проверка status code

```shell
statusCode=$(wget -qSO- --spider localhost:8000 2>&1)
echo $statusCode | grep "200 OK"
```
