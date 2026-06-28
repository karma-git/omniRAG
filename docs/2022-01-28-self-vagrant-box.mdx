---
title: Selfmade Vagrant box
description: VagrantBox собирается настолько же просто как и DockerImage!
slug: selfmade-vagrant-box
authors: [a.horbach]
tags: [vagrant, packer, ansible]
image: https://i.imgur.com/mErPwqL.png
hide_table_of_contents: false
---

# Inspiration

<!-- import tabs -->
import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

На VagrantCloud не нашел нормальных box-ов с GUI.

## Процесс

:::info
Буду делать аналогии с _docker_
:::

### config file

Описываем конфигурацию нашего VagrantBox (_DockerImage_) в формате `.hcl` (_terraform_)

```hcl
source "vagrant" "ubuntu" {
  add_force    = true
  communicator = "ssh"
  provider     = "virtualbox"
  source_path  = "ubuntu/focal64"
}

build {
  name    = "learn-packer"
  sources = [
    "source.vagrant.ubuntu"
  ]
}
```

:::tip
Полезные команды:
```shell
packer validate packer.hcl  # валидирует файл
packer fmt .                # форматирует файлы, и кажется, выполняет валидацию
```
:::

### build

С помощью [`packer`](https://www.packer.io/) (_docker engine_) собираем образ.

```shell
packer build packer.hcl
```

Через некоторое время в директории `learn-packer` появится файл `.box` (_docker_image_)

### push

Заливаем получившийся файл на [VagrantCloud](https://app.vagrantup.com/boxes/search). Понадобиться собрать хэш-сумму файла, например через `md5`

### provisioner

:::note
Любимый провиженер - ansible, но можно использовать `shell`
:::

<Tabs defaultValue="hcl">
<TabItem value="hcl" label="packer.hcl">

```hcl
source "vagrant" "ubuntu" {
  add_force    = true
  communicator = "ssh"
  provider     = "virtualbox"
  source_path  = "ubuntu/focal64"
}

build {
  name    = "learn-packer"
  sources = [
    "source.vagrant.ubuntu"
  ]
  provisioner "ansible" {
    playbook_file = "./ansible/packer-playbook.yml"
  }
}
```

</TabItem>
<TabItem value="yml" label="packer-playbook.yml">

``` yml
---

- name: install docker engine ubuntu
  hosts: all

  become: true
  become_method: sudo

  tasks:
    - name: 1. Update the apt package index and install packages to allow apt to use a repository over HTTPS
      apt:
        name: 
          - apt-transport-https
          - ca-certificates
          - curl
          - gnupg
          - lsb-release
          - python3-pip
          - awscli
        state: latest
        update_cache: true

    - name: 2. Add Docker’s official GPG key
      apt_key:
        url: https://download.docker.com/linux/ubuntu/gpg
        state: present

    - name: 3. Add Docker Repository
      apt_repository:
        repo: deb https://download.docker.com/linux/ubuntu focal stable  # FIXME move to var
        state: present

    - name: 4. Install docker engine
      apt:
        name: docker-ce
        state: latest
        update_cache: true

    # Docker post-install steps for ubuntu

    - name: 1. Make sure that group "docker" exists
      group:
        name: docker
        state: present

    - name: 2. Add aws user to docker docker group
      user:
        name: ubuntu
        groups: docker
        append: true
```

</TabItem>
</Tabs>

### post-processors

:::caution
Не протестировал
:::

Штуки которые выполняются после сборки, например публикация в *VagrantCloud* (_docker push_)

[GitHub repo](https://github.com/karma-git/playground/tree/master/environment/vagrant/ubuntu-gui)

<!--truncate-->
