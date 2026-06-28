---
title: Lens - build from source
description: Notion Fast Start
slug: lens-build
authors: [a.horbach]
tags: [k8s, nodejs]
image: https://i.imgur.com/mErPwqL.png
hide_table_of_contents: false
---

# title

## История

Не запускался Lens 6, быстро проблему решить не получилось, поэтому решил откатиться на предыдущие версии.

```shell
DEBUG=true /Applications/Lens.app/Contents/MacOS/Lens
```
Логи дебага выдавали ошибки, по которым в issues в репозитории на GitHub https://github.com/lensapp/lens не удалось найти полезной информации.

Как выяснилось - легкого доступа к предыдущим релизам нет, единственный из вариантов это собраться из сорцов.

## Сборка

```shell
$ git clone https://github.com/lensapp/lens.git
$ git checkout v5.5.4 # последний из стабильных релизов 5.x.x
$ make build
```
Тут и начинаются грабли, в большей степени связанные с nodejs и несовместимостью версий самой ноды или пакетов.

Мне для корректировки версии помогла утилита `nvm` и эта [статья](https://tecadmin.net/install-nvm-macos-with-homebrew/)

```shell
nvm ls-remote  # смотрим какие варианты нам может предложить менеджер ноды
nvm install lts/fermium # node 15.x
nvm use lts/fermium  # пиним версию ноды в системе
```

В моем случае пина версии ноды хватило, чтобы успешно собрать `.dmg` пакет.
