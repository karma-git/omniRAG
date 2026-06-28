---
id: rust-tools
title: "Rust tools"
sidebar_position: 4
tags:
  - tools
  - rust

---
## Rust tools

### cat -> bat

https://github.com/sharkdp/bat

> A cat(1) clone with wings.

Читаем файл, смотрим **git diff**

![img](https://ah-public-pictures.hb.bizmrg.com/it-happens/bat-git.png)

Печатаем манифест **pod**-а из **etcd**; подсвечиваем синтаксис

![img](https://ah-public-pictures.hb.bizmrg.com/it-happens/bat-2.png)

### du -> dust

https://github.com/bootandy/dust

> A more intuitive version of du in rust

Смотрим **disk usage** выставляя глубину и исключая нежелательные директории

![img](https://ah-public-pictures.hb.bizmrg.com/it-happens/dust-depth.png)

Смотрим сколько места съедают файлы того или иного формата

![img](https://ah-public-pictures.hb.bizmrg.com/it-happens/dust-regex.png)

### find -> fd

https://github.com/sharkdp/fd

> A simple, fast and user-friendly alternative to 'find'

![img](https://raw.githubusercontent.com/sharkdp/fd/master/doc/screencast.svg)

### ls -> exa

https://github.com/ogham/exa

> A modern replacement for 'ls'.

### grep -> ripgrep

https://github.com/BurntSushi/ripgrep

> ripgrep recursively searches directories for a regex pattern while respecting your gitignore

Поищем в каких файлах остались **TODO**-шки

![img](https://ah-public-pictures.hb.bizmrg.com/it-happens/rg-2.png)

## Hacks

```shell
alias cat=bat
alias du=dust
alias find=fd
alias ls=exa
alias grep=rg

fd . -X bat  # open all files inside the current dirctory via bat
k get po -n kube-system aws-node-4dvzk -o yaml | bat --language=yaml  # print k8s object manifest with syntax highlights
```

... to be continued
