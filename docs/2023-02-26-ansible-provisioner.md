---
title: "ansible provisioner для terraform"
tags:
  - aws
  - gcp
  - terraform
  - ansible
date: 2023-02-26
---

# ansible provisioner для terraform

При использовании подхода IaC к развертыванию compute мощностей, происходит 2 этапа:
- bootstrapping - это получение ресурсов по требованию (terraform код) у облачного провайдера
- provisioning - это конфигурирование (как правило ОС) полученных ресурсов

**взято из статьи про** [`pl-engineering`](/blog/2022/11/23/pl-engineering)

Попробуем решить простую задачу - поднять виртуальную машину и установить на нее nginx


## common

Общие ресурсы - локальные tf переменные и anisble playbook

```terraform
locals {
  // $ ssh-keygen -t ed25519 -f ~/.ssh/ansible -C ansible
  ssh_keys = [
    {
      user             = "ansible"
      private_key_path = "~/.ssh/ansible"
      public_key_path  = "~/.ssh/ansible.pub"
    },
  ]
  // ansible alias
  ssh = local.ssh_keys[0]

  author = "ahorbach"
}

```

```yaml
---

- name: Workshop aws,gcp,terraform,ansible
  hosts: all
  vars: {}

  become: true
  become_method: sudo

  tasks:
    - name: Ensure Nginx is at the latest version
      apt:
        name: nginx
        state: latest
        update_cache: true

    - name: Make sure Nginx is running
      systemd:
        name: nginx
        state: started
```

## AWS

### 1. provider

Сконфигурируем provider:

```terraform
provider "aws" {
  region  = "eu-west-1"
  profile = var.aws_named_profile
}
```

### 2. data

Инициализируем Data Sources, чтобы найти id стандартной VPC, подсети в этой vpc, а также id свежего AMI для ubuntu:

```terraform
data "aws_vpc" "default" {
  default = true
}

data "aws_subnet_ids" "default" {
  vpc_id = data.aws_vpc.default.id
}

data "aws_ami" "ubuntu" {
  most_recent = true
  owners      = ["099720109477"] // Canonical

  filter {
    name   = "description"
    values = ["Canonical, Ubuntu, 20.04 LTS, amd64 focal image build on*"]
  }

  filter {
    name   = "virtualization-type"
    values = ["hvm"]
  }
}
```

### 3. aws_security_group, aws_key_pair

Создадим security group - сервер сможет слать любой траффик в интернет, а из публичного интернета будет доступ по 22 (ssh) и 80 (http) портам

```terraform
resource "aws_security_group" "this" {
  name        = "${local.author}-sg"
  description = "Allow ssh and web on port 80, and answer to everyone"
  vpc_id      = data.aws_vpc.default.id

  ingress {
    // ssh
    protocol    = "tcp"
    from_port   = 22
    to_port     = 22
    cidr_blocks = ["0.0.0.0/0"]
  }

  ingress {
    // web
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  egress {
    // Allow outgoing traffic from all ports
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}
```

Добавим публичную часть нашего ssh ключа в aws:

```terraform
resource "aws_key_pair" "this" {
  key_name   = "${local.author}-ansible"
  public_key = file(local.ssh.public_key_path)
}
```

### 4. aws_instance

```terraform
resource "aws_instance" "this" {
  ami           = data.aws_ami.ubuntu.id
  instance_type = "t2.micro"

  vpc_security_group_ids = [aws_security_group.this.id]
  availability_zone      = "eu-west-1b"

  associate_public_ip_address = true
  key_name                    = aws_key_pair.this.key_name

  provisioner "remote-exec" { # (1)
    script = <<EOF
      #!/bin/bash

      while [ ! -f /var/lib/cloud/instance/boot-finished ]; do
        echo -e "\033[1;36mWaiting for cloud-init..."
        sleep 1
      done
    EOF

    connection {
      type        = "ssh"
      host        = self.public_ip
      user        = "ubuntu"
      private_key = file(local.ssh.private_key_path)
    }
  }

  provisioner "local-exec" { # (2)
    command = <<EOF
        ansible-playbook \
          --inventory '${self.public_ip},' \
          --private-key ${local.ssh.private_key_path} \
          --user ubuntu \
          ./playbook.yml
        EOF

  }
  tags = {
    Name = "${local.author}-nginx"
  }
}
```

1. Прежде чем прокатывать ansible-playbook, мы ждем пока облако (aws), скажет, что VM готова к использованию
2. Прокатываем ansible-playbook, фактически это происходит с хоста, откуда мы выполняем `terraform apply`

## GCP

### 1. provider

```terraform
provider "google" {
  project = var.gcp_project_id
  region  = "europe-central2"
  zone    = "europe-central2-b"
}
```

### 2. google_compute_firewall, google_os_login_ssh_public_key

Сделаем SA, и аналогичный aws-овской SG фаервол

```terraform
data "google_client_openid_userinfo" "ahorbach" {}


resource "google_service_account" "this" {
  account_id = "${var.gcp_project_id}-nginx"
}

resource "google_compute_firewall" "web" {
  name    = "web-access"
  network = local.network

  allow {
    protocol = "tcp"
    ports    = ["80"]
  }
  source_ranges = ["0.0.0.0/0"]

  target_service_accounts = [google_service_account.this.email]
}
```

Добавим публичную часть нашего ssh ключа в gcp:

```terraform
resource "google_os_login_ssh_public_key" "this" {
  project = var.gcp_project_id
  user    = data.google_client_openid_userinfo.ahorbach.email
  key     = file(local.ssh.public_key_path)
}
```

### 3. google_compute_instance

Запустим виртуальную машину:

```terraform
resource "google_compute_instance" "this" {
  name         = "${local.author}-nginx"
  machine_type = "e2-micro"
  zone         = "europe-central2-b"

  boot_disk {
    initialize_params {
      image = "ubuntu-2004-focal-v20230213"
    }
  }

  network_interface {
    network = local.network
    access_config {}
  }

  service_account {
    email  = google_service_account.this.email
    scopes = ["cloud-platform"]
  }

  // creater users and put public keys
  metadata = {
    ssh-keys = join("\n", [for key in local.ssh_keys : "${key.user}:${file(key.public_key_path)}"])
  }

  provisioner "remote-exec" {
    inline = ["echo 'Waint until SSH is ready'"]

    connection {
      type        = "ssh"
      user        = local.ssh.user
      private_key = file(local.ssh.private_key_path)
      host = self.network_interface.0.access_config.0.nat_ip
    }
  }

  provisioner "local-exec" {
    command = <<EOF
        ansible-playbook \
          --inventory '${self.network_interface.0.access_config.0.nat_ip},' \
          --private-key ${local.ssh.private_key_path} \
          --user ${local.ssh.user} \
          ./playbook.yml
        EOF
  }
}
```

## Выводы, ссылки

- В разных облаках можно сконфигурировать ОС виртуальных машин при помощи одних и тех же ansible playbooks
- Конфигурирование через ansible не всегда оправдано, есть и другие способы: сборку image-а через packer + ansible, и последующее использование этого образа. Либо configuration management утилиты, работающий по моделе pull (например `ansible-pull`)
- ansible provisioner, это эквивалент команды `ansible-playbook --inventory '34.118.12.194,' --private-key ansible --user ansbile playbook.yml`, которую terraform запустит локально после `terraform apply`
- Source code: https://github.com/karma-git/kb/tree/master/lessons/001, [кликабельная ссылка](https://github.com/karma-git/kb/tree/master/lessons/001)
