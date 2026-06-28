---
id: nana-sre
title: What is SRE
sidebar_position: 1
---
# Site Reliability Engineering (SRE)

export const Highlight = ({children, color}) => (
  <span
    style={{
      backgroundColor: color,
      borderRadius: '2px',
      color: '#fff',
      padding: '0.2rem',
    }}>
    {children}
  </span>
);

:::info sre
Hope is not a strategy
:::

[Nana Janashia](https://www.linkedin.com/in/nana-janashia/)

<div class="video-wrapper">
  <iframe  height="540" frameborder="0" allowfullscreen width="100%" src="https://www.youtube.com/embed/OnK4IKgLl24" frameborder="0" allowfullscreen></iframe>
</div>

## Why was there a need for SRE?

**Dev**elopers - хотят выкатывать новые релизы, **Op**eration**s** - поддерживать систему в стабильном состоянии. Их конфликт интересов должен решить **DevOps**.

Но есть нестыковка:
- <Highlight color="#25c2a0">DevOps</Highlight> - методология сосредоточена на скорость разработки, а не про стабильность и надежность.
- Нету выделенной роли которая концентрируется на стабильности систем.

## What is SRE? - Official Definition

<Highlight color="#25c2a0">SRE</Highlight> - разработчики которые относятся к процессам оперирования как к разработке, для обеспечения надежности систем.

## What is system reliability and why it's important?
Что такое "**system**", о которой заботятся SRE -> Whole Deployment Environment:

- infrastructure: servers,cloud,virtualization,networks,databases
- applications and services

Что такое "**Reliable**" services -> критичные сервисы (gmail,youtube) которые редко бывают недоступны.

> Пользователи не замечают надежность, они замечают только проблемы - а это чревато потерей пользователей и прибыли

## How to make systems reliable?

Как сделать систему надежной? Избавиться от того что делает ее ненадежной -> Изменения:
- изменения инфрастуктуры
- изменения платформы (k8s)
- изменения сервисов и приложений

Кажется что нужно остановить изменения, но лучше лишь ограничить, потому что изменения.

**SRE** призван автоматизировать сложный и бюрократизированный процесс внесения изменений.

## SRE in Practice: SLA & Error Budget

**Service Level Agreement (SLA)** - договоренность между провайдером услуг и его клиентами о том насколько сервис надежен.

Availability / Errors = %, обычно измеряется количество 9-ок после запятой

[SLA table](https://en.wikipedia.org/wiki/High_availability)

|Availability %|Downtime per year|Downtime per quarter|Downtime per month|Downtime per week|Downtime per day (24 hours)|
|--------------|-----------------|--------------------|------------------|-----------------|---------------------------|
|99% ("two nines")|3.65 days|21.9 hours|7.31 hours|1.68 hours|14.40 minutes|
|99.9% ("three nines")|8.77 hours|2.19 hours|43.83 minutes|10.08 minutes|1.44 minutes|
|99.99% ("four nines")|52.60 minutes|13.15 minutes|4.38 minutes|1.01 minutes|8.64 seconds|
|99.999% ("five nines")|5.26 minutes|1.31 minutes|26.30 seconds|6.05 seconds|864.00 milliseconds|

Может предоставляться для различных показателей, например:
- Availability (отсутствие даунтайма)
- Количество http ошибок - SLA 99 % - 1_000_000 requests per week -> 990_000 - not 5xx
- Latency
- ... etc

SLA определяет бизнес + инженеры вместе. Если вы не в SLA - приостанавливается работа над фичами, и активизируется работа над обеспечением надежности системы, до тех пор пока не вернемся в SLA. Это простой путь регулировки скорости релизов.

**Error Budget** - это те 10_000 5ХХ ошибок которые мы могли словить за неделю, или N минут даунтайма. Их можно потратить на рискованные изменения или устроить хаос инженеринг.

## SRE Tasks and Responsibilities

- Automation
- Процессы разрешения релиза или запрета в зависимости от SLA
- Observability - Monitoring, Logging, Alerting
- Hight Availability
- Reliability
- Self Healing

Главная цель - снизить радиус поражения от проблем. **Outage** - это полезный опыт -> **blameless postmortem**.
