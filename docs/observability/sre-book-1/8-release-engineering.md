---
id: 8-release-engineering
title: Chapter 8.  Release Engineering
sidebar_position: 8
---

# Chapter 8.  Release Engineering

- Machine: A piece of hardware (or perhaps a VM)
- Server: A piece of software that implements a 
service

Градация: machine in rack-unit,rack,row,cluster(logical),dc,campus(eg. availability zone)

Сеть: Jupiter(фабрика коммутаторов с bandwidth ~1.3 Пб/с).

## Build

Для сборки используется использует Blaze - это алиас для [Bazel](https://bazel.build/start/bazel-intro)

<details>
<summary>Пример конфигурационного файла `BUILD` </summary>

```bazel
package(default_visibility = ["//visibility:public"])

cc_library(
    name = "hello-lib",
    srcs = ["hello-lib.cc"],
    hdrs = ["hello-lib.h"],
)

cc_binary(
    name = "hello-world",
    srcs = ["hello-world.cc"],
    deps = [":hello-lib"],
)

cc_test(
    name = "hello-success_test",
    srcs = ["hello-world.cc"],
    deps = [":hello-lib"],
)

cc_test(
    name = "hello-fail_test",
    srcs = ["hello-fail.cc"],
    deps = [":hello-lib"],
)

filegroup(
    name = "srcs",
    srcs = glob(["**"]),
)
```

</details>

## Packages - MPM

Используется Midas (MPM) - внутренний менеджер пакетов google.

Артефакты тегируются версией релиза и дополнительно окружением назначения (dev, canary, production)

## Rapid

Местный CI/CD инструмент:

![rapid](https://ah-public-pictures.hb.bizmrg.com/sre/sre-book/p8-rapid.png)

## Deployment

Rapid в простых случаях, при прохождении тестов (push on green) может развернуть новый релиз в production окружение.

В других случаях используется Sisyphus - фреймворк на python который принимает решения об развертывании.

## Key Insights

<details>
<summary>Symlinks</summary>

- [How Embracing Continuous Release Reduced Change Complexity](http://usenix.org/conference/ures14west/summit-program/presentation/dickson), USENIX Release Engineering Summit West 2014, [Dic14]
-[ Maintaining Consistency in a Massively Parallel Environment](https://www.usenix.org/conference/ucms13/summit-program/presentation/mcnutt), USENIX Configura‐ tion Management Summit 2013, [McN13]
- [The 10 Commandments of Release Engineering](https://www.youtube.com/watch?v=RNMjYV_UsQ8), 2nd International Workshop on Release Engineering 2014, [McN14b]
- [Distributing Software in a Massively Parallel Environment](https://www.usenix.org/conference/lisa14/conference-program/presentation/mcnutt), LISA 2014, [McN14c]

</details>

:::note

Empty

:::
