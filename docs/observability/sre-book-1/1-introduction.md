---
id: 1-introduction.md
title: Chapter 1.  Introduction
sidebar_position: 1
---

# Chapter 1.  Introduction

<!-- ### The Sysadmin Approach to Service Management -->

Hope is not  a strategy (Traditional SRE saying).

## Google’s Approach to Service Management: Site Reliability Engineering

What is SRE -> my explanation is simple: SRE is what happens when you ask a software engineer to design an operations team.

В google SRE команда это про разработку, у них есть трешхолд 50% времени должно уходить на разработку, 50% на ручные операции по поддержанию сервиса.

## Tenets of SRE

- availability
- latency 
- performance 
- efficiency 
- change management
- monitoring 
- emergency response
- capacity planning

### Ensuring a Durable Focus on Engineering

Если трешхолд на 50% переполняется, задачи редиректятся обратно на разработчиков, их привлекают к дежурствам и т.д. Все (dev,ops teams) должны понимать зачем это - снижение операционной работы.
 
**Postmortem**-ы должны быть написаны на все инциденты: для улучшения обработки в случае повторения и плана действий по устранению. Для такого частого написания должна быть *blameless*-культура.

#### Pursuing Maximum Change Velocity Without Violating a Service’s SLO

Конфликт Dev и Ops: первые хотят делать улучшения продукта и часто выпускать новые фичи. Из-за этого может страдать надежность за которую отвечают Ops и они в свою очередь не хотят фичи. Для этого введен *error budget* (100% is the wrong reliability target). *error budget* - должен выставить продукт, так чтобы пользователи продукта были удовлетворены. В идеальном мире *error budget* можно **тратить** на рискованные деплойменты. Недотупность - это теперь не "плохая" штука - а то чем dev и ops могут **управлять**.

### Monitoring

Мониторинг не должен требовать от человека никаких действий - интерпретацию наблюдений должно осуществлять ПО, люди нужны только в том случае если от них требуются какие либо действия.

- Alerts - нужно немедленно отреагировать
- Tickets - нужен посмотреть, но не срочно
- Logging - диагностическая инфа, по умолчанию сюда не нужно смотреть

### Emergency Response

Надежность - это функция от среднего времени безотказной работы (meantime to failure, MTTF) и среднего времени восстановления (mean time of repair, MTTR):

$$
observability = \frac {MTTF} {MTTR}
$$

Наличие плана действия: runbook | playbook помогает дежурному инженеру быстрее решать проблему, но тем не менее инженер должен быть готов к неожиданностям. В google есть практические упражнения на устранение аварий: **“Wheel of Misfortune”**

### Change Management

SRE has found that roughly **70%** of outages are due to changes in a live system.

- Implementing progressive rollouts
- Quickly and accurately detecting problems
- Rolling back changes safely when problems arise

Усталость, расслабленность, пренебрежение и невнимательность - эти человеческие факторы должны быть побеждены автоматизацией.

### Demand Forecasting and Capacity Planning

Система должна иметь достаточную производительность чтобы обеспечивать заданный показатель доступности. Для этого нужно предпринимать следующие шаги:

- прогнозирование роста
- push-и
- нагрузочное тестирование

### Provisioning

Провиженинг и бустрапинг новых инстансов в ЦОД-е или облаке тоже сопряжено с некоторыми рисками.

### Efficiency and Performance

SRE должны следить за утилизацией ресурсов и таким образом думать о костах.

## The End of the Beginning

“as a software engineer, this is how I would want to invest my time to accomplish a set of repetitive tasks”
