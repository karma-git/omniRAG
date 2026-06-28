---
id: 0-abbreviations-foreword.md
title: Abbreviations & Part 0.  Foreword
sidebar_position: 0
---

![sre-book](https://ah-public-pictures.hb.bizmrg.com/sre/sre-book/SRE-book.jpeg)

https://g.co/SREbook

## abbreviations

- Change List (**CL**) - список изменений
- Google File System (GFS)
- BandwidthEnforcer (BwE)
- Global Software Load Balabcer (GSLB) - балансировщик нагрузки
- GFE - Google Frontend - обратный прокси сервер, держит tcp - соединение с клиентом и с приложением
- FE - frontend - что-то клиентское (доступное для конечного пользователя), говорит о публичных IP адресах
- BE - backend - наооборот
- RPC - Remote Procedure Call - протокол удаленного вызова процедур
- BNS - Borg Naming Service - адрес до экземпляра приложения <!-- ссылка на p2 -->
- EB - Error Budget - сколько времени сервис может "лежать", основывается на SLO
- MTTR - mean time to repair - среднее время восстановления (disaster recovery)
- SOA - service-oriented-architecture - то набор архитектурных принципов, не зависящих от технологий и продуктов, совсем как полиморфизм или инкапсуляция.
- [MPM](https://luke.carrier.im/notes/549119f2-27aa-4bbb-b4cc-9634b001d477/) - midas package manager -  внутренний менеджер пакетов google.
- TSDB - time series database - БД, оптимизированная для хранения временных рядов

## Parts

...

### Part II - Принципы

- Риски
- SLO, SLA, SLI
- метрики и мониторинг
- toil и автоматизация

### Part III - Практики

Пирамида надежности:

![img](https://ah-public-pictures.hb.bizmrg.com/sre/sre-book/p3-reliability-pyramid.png)

## Chapter 0.  Foreword

### Foreword

В 2000-x Системное Администрирование - это еще не **engineering**, и это направление как будто в тупике.

Разработка ПО - это как рождения ребенка, сложно, но после появления на свет становится еще сложнее. **SRE-инженер** обеспечиваю *надежность* ПО для (обслуживания | написания системной части ПО: бэкапы, балансировка нагрузки). **Human Error** это нечто неотвратимое и это нужно принять (кейс с Аполлоном-8)

### Convention

- bold - highlighting by author
- italic - highlighting by book authors 
<!-- - code - -->
- codeblock - listing
- admotion (tip, info, caution)
