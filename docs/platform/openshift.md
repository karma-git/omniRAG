---
id: open-shift-quick-look
title: "OpenShift QuickLook"
sidebar_position: 5
tags:
  - platform
  - k8s

---

:::caution

Мысли в статье - это конспект + домыслы автора после 7 минутного ролика про OpenShift

:::

![img](https://ah-public-pictures.hb.bizmrg.com/it-happens/openshift.png)

## Layers

1. RedHat OS
2. K8s layer
3. OpenShift aka platform?

## Workflow

1. Разработчик пушит изменения в git
2. CI / CD (сборка образа и доставка его в реджистри)
3. / / CD - деплоймент в OpenShift средствами CI
4. Operational: взаимодействие с api через новый клиент (cli) + GUI (новый Lens?)
5. Operational+: какая-то интеграция с GUI OpenShift-а aka ansible tower для уходом за воркерами

По сути OpenShift - это то, что в моей текущей компании называется **платформа** или обвесы (приложения) на куб, которые позволяют разработчикам удобно работать с инфраструктурой, а также CI / CD процессы вокруг этой платформы.

<div class="video-wrapper">
  <iframe height="540" frameBorder="0" allowFullScreen width="100%" src="https://www.youtube.com/embed/KTN_QBuDplo"></iframe>
</div>
