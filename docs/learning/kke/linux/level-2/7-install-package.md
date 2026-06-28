---
title: "7 - Install a package"
tags:
  - kodekloud-engineer-sysadmin
---

## Task


As per new application requirements shared by the Nautilus project development team, serveral new packages need to be installed on all app servers in Stratos Datacenter. Most of them are completed except for samba.

Therefore, install the samba package on all app-servers.

## Solution

```shell
# Создайте массив с данными серверов и их учетными данными
servers=(
  "stapp01 tony   Ir0nM@n"
  "stapp02 steve 	Am3ric@"
  "stapp03 banner BigGr33n"
  # Добавьте остальные серверы по аналогии
)

# Цикл для установки Samba на каждом сервере
for server_info in "${servers[@]}"; do
  # Разделите строку с информацией о сервере на компоненты
  read -r server username password <<< "$server_info"

  # Выполните установку Samba на сервере
  sshpass -p "$password" ssh "$username@$server" 'sudo yum update -y && sudo yum install -y samba'
  # ssh "steve@stapp02" 'sudo yum install -y samba'

  # Если вы используете другой пакетный менеджер или ОС, измените команду выше в соответствии с ней
done
```
