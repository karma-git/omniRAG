---
id: 3-risks
title: Chapter 3.  Embracing Risk
sidebar_position: 3
---

# Chapter 3.  Embracing Risk

100% это недостижимая цифры, стремление к ней невероятно дорогое удовольствие и ко всему прочему вредит так же и пользователю - супер-пупер надежную систему сложнее мэйтенить, доставлять новые фичи что в конечном счете сказывается на пользователях.

## Managing Risk

надежность (reliability), доступность (availability), 99.9% - SLO (Service Level Objective):
- стоимость избыточных вычислительных мощностей
- стоимость времени инженеров на проектирование и поддержку

Не нужно делать сервис надежнее необходимого.

## Measuring Service Risk

Нужно определить SLO для сервиса, это нужно сделать вместе с бизнесом на основе ожиданий пользователей к сервису.

Формулы:

$$
availability = \frac {uptime} {uptime + downtime}
$$

доступность - это отношение времени безотказной работы к времени безотказной работы + времени простоя

$$
availability = \frac {successful request} {total request}
$$

доступность - это отношение успешно обработанных запросов к общему количеству запросов.

SLO удобно выставлять для квартала (Q)

## Risk Tolerance of Services

Ситуация когда есть сервисы для определения понятия надежности к которым нужно работать инженерам вместе с бизнесам. Также такие сервисы могу не иметь четкого владельца.

В *инфрастуктуре* все +- так же

### Target level of availability

- What level of service will the users expect?
- Does this service tie directly to revenue (either  our revenue, or our customers’ revenue)?
- Is this a paid service, or is it free?
- If there are competitors in the marketplace, what level of service do those com‐ petitors provide?
- Is this service targeted at consumers, or at enterprises?

**Типы сбоев**: короткие / длинные отключения.

**Costs**: нужно считать при добавлении еще одной 0.09% - превысит ли прибыль увеличения надежности затраты на инфру?

## Motivation for Error Budgets

Предпосылки к созданию типичный конфликт DevOps - выкатка новых фич vs стабильность. Список наиболее типичных спорных моментов:

- Software fault tolerance (Устойчивость к сбоям)
- Testing (Тестирование)
- Push frequency (Частота выпуска новых версий)
- Canary duration and size (Продолжительность тестирования и размер выборки)

**Error Budget (EB)** - объективный показатель с помощью которого командам с противоположными интересами проще вести диалог.

EB строиться на основе SLO (Service Level Objective).

Алгоритм создания EB:
- Product Management defines an SLO, which sets an expectation of how much uptime the service should have per quarter.
- The actual uptime is measured by a neutral third party: our monitoring system.
- The difference between these two numbers is the “budget” of how much “unreli‐ ability” is remaining for the quarter.
- As long as the uptime measured is above the SLO—in other words, as long as there is error budget remaining—new releases can be pushed.

## Key Insights

<details>
<summary>Symlinks</summary>

<!-- TODO: -->
- SLO - (4)

</details>

:::note

- Управление надежностью сервиса в основном заключается в управлении рисками.
- Практически никогда не стоит планировать 100%-ый уровень надежности: его нельзя достигнуть, пользователь может не нуждаться в нем, сложный мэйтененс уменьшит количество релизов и т.о. пострадает пользователь. Необходимо соотнести назначение и особенности сервиса с теми рисками, которые бизнес готов на себя взять. 
- Введение EB стимулирует команды SRE и разработчиков и подчеркивает их общую ответственность за систему. Он позволяет проще принимать решения о скорости выпуска новых версий и эффективно сглаживать конфликт между участниками проекта в случае сбоев, а также дает возможность нескольким командам без лишних эмоций приходить к одинаковым выводам о рисках при выпуске продукта
:::
