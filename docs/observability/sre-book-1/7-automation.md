---
id: 7-automation
title: Chapter 7.  The Evolution of Automation at Google
sidebar_position: 7
---

# Chapter 7.  The Evolution of Automation at Google

Besides black art, there is only automation and mechanization.

## The Value of Automation

- Consistency (постоянство) - единообразное выполнение одних и тех же действий.
- A platform - как единая точка для автоматизации и устранения ошибок
- Faster Repairs - снижение MTTR
- Faster Action - e.g. скрипт который решает проблему
- Time Saving - проблема быстро решается

## A Hierarchy of Automation Classes

1) No automation
Database master is failed over manually between locations.
2) Externally maintained system-specific automation
An SRE has a failover script in his or her home directory.
3) Externally maintained generic automation
The SRE adds database support to a “generic failover” script that everyone uses.
4) Internally maintained system-specific automation
The database ships with its own failover script.
5) Systems that don’t need any automation
The database notices problems, and automatically fails over without human intervention.

- ручные операции
- автоматизация (скрипты / ansible)
- автономность (borg)

## Detecting Inconsistencies with Prodtest

Prodtest - юнит-тесты на python которые проверяют конфигурацию кластера на соотвествие с желаемой

![prod-test](https://ah-public-pictures.hb.bizmrg.com/sre/sre-book/p7-prodtest.png)

Со временем к тестом добавили функцию исправления найденных проблем, запуски сделали идемпотентными, что позволило запускать сценарий периодически.

![prod-test-fix](https://ah-public-pictures.hb.bizmrg.com/sre/sre-book/p7-prodtest-fix.png)

## Key Insights

<details>
<summary>Symlinks</summary>

<!-- TODO: -->
-  Accelerating SREs to On-Call and Beyond - (28)

- https://www.engineyard.com/blog/pets-vs-cattle/
- https://xkcd.com/1205/
- https://en.wikipedia.org/wiki/Air_France_Flight_447

</details>

:::note

Empty

:::
