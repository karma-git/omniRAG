---
title: Terraformer - reverse Terraform
description: Terraformer - reverse Terraform
slug: terraformer
authors: [a.horbach]
tags: [aws, terraform]
image: https://i.imgur.com/mErPwqL.png
hide_table_of_contents: false

---

# title

## Описание

https://github.com/GoogleCloudPlatform/terraformer

**Terraformer** - тулза преобразующая существующие облачные ресурсы в `terraform код`. Может быть полезна в различных кейсах, например: при обучении aws-у и terraform-у - создали ресурсы через console по курсу, а потом дампнули это в terraform код. Либо более классический кейс - описываете существующую инфраструктуру в IaC.

## Использование

:::info

запустить получилось вот так, но это вряд ли best practices

:::

Экспортируем креды доступа к aws-apo

```shell
export AWS_DEFAULT_PROFILE=my-profile  # ~/.aws/credentials
export AWS_ACCESS_KEY_ID=id
export AWS_SECRET_ACCESS_KEY=key
```

Так же нам нужен tf провайдер `aws`:

```hcl
terraform {
  required_version = ">= 1.3.0"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "4.42.0"
    }
  }
}
```

Инициализируем провайдер, запускаем terraformer и натравливаем на нужный нам aws ресурс

```shell
terraform init # инициализируем провайдер в директорию ./.terraform
terraformer import aws --resources=route53 --regions=us-east-1 --profile my-profile
terraformer import aws --resources=route53 --regions=us-east-1 --profile my-profile --filter="Type=route53_zone;Name=tags.Name;Value=my.example.com"
```
