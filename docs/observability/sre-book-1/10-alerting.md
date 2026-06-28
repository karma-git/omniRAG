---
id: 10-alerting
title: Chapter 10.  Practical Alerting from Time-Series Data
sidebar_position: 10
---

# Chapter 10.  Practical Alerting from Time-Series Data

*"May the queries flow, and the pager stay silent."*

Благодаря мониторингу владельцы сервиса могут оценивать влияние изменений, реагировать на критические ситуации, измерять бизнес метрики.

Borgmon это очень похожая на Prometheus система мониторинга, родилась сразу за Borg-ом

## Instrumentation of Applications

В google в свое приложение легко встроить http handler **/varz**

```shell
% curl http://webserver:80/varz 
http_requests 37
errors_total 12
http_responses map:code 200:25 404:0 500:12
```

Для мониторинга был выбран протокол http, т.к. smtp более низкоуровневый, а реальный приросте надежности при передаче незначителен

## Storage in the Time-Series Arena

Данные хранятся в in-memory database, и периодически дампаются на диски (aka redis).

Так выглядит **time-series Arena**:

![img](https://ah-public-pictures.hb.bizmrg.com/sre/sre-book/c10-tsarea.png)

Это матрица метрики, которая с течением времени разрастается по вертикали, точки на картинке - это данные которые записываются в формате `(timestamp, value)`

Каждая такая time-series, имеет свои уникальные label-s, в формате `name=value`

Точки на графике выше записываются в TSDB в формате (timestamp, value)

## Labels and Vectors

> Сложная тема, сомневаюсь, что я сумел ее правильно раскрыть

Вектор: time-series are stored as sequences of numbers and timestamps, which are referred to as vectors. Like vectors in linear algebra, these vectors are slices and cross-sections of the multidimensional matrix of data points in the arena

![img](https://ah-public-pictures.hb.bizmrg.com/sre/sre-book/c10-vectors.png)

Имя time-series-ии это **labelset**, потому что она реализована как набор label-ов представляющих собой пары key=value. Одна из этих меток содержит имеет ключ name, значение которого и "*обзывает*" time-series-ию

Некоторые метки важны, они нужны для того чтобы достать таймсерию из TSDB, например:

```shell
# в случае с BorgMon - имя таймсерии, очевидно, это var
{var=http_requests,job=webserver,service=web,zone=us-west}
```

Результат этого запроса - вектор.

Если в мониторинге есть несколько векторов соответствующих запросу, может вернуться побольше:

```shell
{var=http_requests,job=webserver,instance=host0:80,service=web,zone=us-west} 10
{var=http_requests,job=webserver,instance=host1:80,service=web,zone=us-west} 9
{var=http_requests,job=webserver,instance=host2:80,service=web,zone=us-west} 11
{var=http_requests,job=webserver,instance=host3:80,service=web,zone=us-west} 0
{var=http_requests,job=webserver,instance=host4:80,service=web,zone=us-west} 10
```

Так же можно сделать срез из time-series arena, запросив векторы только за определенный момент:

```shell
# запрос
{var=http_requests,job=webserver,service=web,zone=us-west}[10m]
# результат
{var=http_requests,job=webserver,instance=host0:80, ...} 0 1 2 3 4 5 6 7 8 9 10
{var=http_requests,job=webserver,instance=host1:80, ...} 0 1 2 3 4 4 5 6 7 8 9
{var=http_requests,job=webserver,instance=host2:80, ...} 0 1 2 3 5 6 7 8 9 9 11
{var=http_requests,job=webserver,instance=host3:80, ...} 0 0 0 0 0 0 0 0 0 0 0
{var=http_requests,job=webserver,instance=host4:80, ...} 0 1 2 3 4 5 6 7 8 9 10
```

The name of a time-series is a labelset, because it’s implemented as a set of labels expressed as key=value pairs. One of these labels is the variable name itself, the key that appears on the varz page.

## WIP

...

## Key Insights

<details>
<summary>Symlinks</summary>

<!-- TODO: -->
- WIP

</details>

:::note

Empty

:::
