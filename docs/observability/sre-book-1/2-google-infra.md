---
id: 2-google-infra
title: Chapter 2.  Google Infra
sidebar_position: 2
---

# Chapter 2.  The Production Environment at Google, from the Viewpoint of an SRE

- Machine: A piece of hardware (or perhaps a VM)
- Server: A piece of software that implements a 
service

Градация: machine in rack-unit,rack,row,cluster(logical),dc,campus(eg. availability zone)

Сеть: Jupiter(фабрика коммутаторов с bandwidth ~1.3 Пб/с).

**Borg**

### Managing Machines

![img](https://ah-public-pictures.hb.bizmrg.com/sre/sre-book/p2-borg-architecture.png)

Borg (похож на mesos) - он оперирует **job**-ами, это может быть запуск демона и etc. Borg шедулид джобы на разные ноды и следит за то чтобы они там выполнялись (scheduler,kubelet).

Обращение в job-е идет по BNS(Borg Naming Service) имени: `/bns/<cluster>/<user>/<job name>/<task number>`, BNS резоливится в `<IP address>:<port>` (k8s - `<svc-name>.<ns>.svc.cluster.local` kube-dns или `<svc-name>.<ns>:<port>` для доступа внутри куба)

Scheduler как и в k8s следит за ресурсами которые запрашивает job-а, а так же старается назначать джобы на машины в разных стойках.

### Storage

![img](https://ah-public-pictures.hb.bizmrg.com/sre/sre-book/p2-storage.png)

СХД от google для Borg-а можно сравнить с Lustre и [Hadoop Distributed File System (HDFS)](https://habr.com/ru/post/42858/)

### Networking

Для построения сети использует протокол OpenFlow ([wiki](https://en.wikipedia.org/wiki/OpenFlow), [habr](https://habr.com/ru/company/etegro/blog/245037/)) - это контроллер который программно управляет сетевыми железяками.

Некоторые сервисы геораспределены, используется балансировка на трех уровнях:
- geo DNS
- на уровне сервисов
- gRPC

## Other System Software

### Lock Service

**Chubby** - сервис блокировок, использует протокол Paxos и асинхронно обращается к Consensus.

Используется, например для выбора мастера, если например у нас есть 5 реплик, но единовременно мастером может быть только одна из них.

### Monitoring and Alerting - **Borgmon**

Местный прометеей.

### swe infra / environment 

Сервисы между собой общаются через **Stubby** - это местная версия gRPC. Данные передаются через protocol buffers = protobufs (аналог XML) 

Все разработчики работают в монорепе и активно шлют MR-ы в соседние сервисы, если находят там что-то.

Push-on-Green - это местный CD когда при прохождении автотестов идет деплой в прод.

### Shakespeare (сервис - пример)

Сервис, который помогает определить в каких произведениях шекспира находится указанное вами слово.

- БД (bigtable) где лежат данные (тексты)
- frontend: обрабатывает запросы клиентов

MapReduce:
- The mapping phase reads Shakespeare’s texts and splits them into individual words. This is faster if performed in parallel by multiple workers.
- The shuffle phase sorts the tuples by word.
- In the reduce phase, a tuple of (word, list of locations) is created.

Каждый кортеж записывается в виде строки в bigtable, ключ - слово

### Lifecycle of a Request

![img](https://ah-public-pictures.hb.bizmrg.com/sre/sre-book/p2-request-lifecycle.png)

1. Клиент делает запрос на URL сервиса. DNS сервис google резолвит DNS-запрос в адрес GFE при помощи GSLB
2. Запрос клиента попадает на GFE
3. GFE при помощи GSLB находит FE приложения и передает ему данные через RPC
4. FE связывается с BE приложения и передает данные через protobuf (местный JSON). Найти экземпляр BE (BNS адрес) помогает GSLB
5. BE идет в базу (в этом случае в Bigtable) достает данные и они возвращаются клиенту

### QoS

Зная примерное количество запросов в секунду которое может обрабатывать один экземпляр бэкэнда приложения - вычисляем сколько нужно и как их географически разнести. Как геораспределенные бэки будут ходить в базу.

## Key Insights

<details>
<summary>Symlinks</summary>

<!-- TODO: -->
- blobstore - (26)
- geo DNS - (19)
- gRPC - (20)
- Chubby - (23)

</details>

:::note

Empty

:::
