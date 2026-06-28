---
title: Kubed - secret sync between k8s clusters in different aws accounts
description: Kubed - secret sync between k8s clusters in different aws accounts
slug: kubed-cross-sync
authors: [a.horbach]
tags: [aws, k8s]
image: https://i.imgur.com/mErPwqL.png
hide_table_of_contents: false

---

# title

## История, Архитектура

### 1) aws account mc-legacy

![img](https://ah-public-pictures.hb.bizmrg.com/it-happens/kubed-cross-sync-1.jpeg)

Имеется legacy приложение в aws аккаунте:

1. В route53 зарегистрирован домен `<my-company>.io` и аналогичная hosted zone
2. В зоне есть запись `<my-service>.<my-company>.io` , смотрит на `<lb>.<my-company>.io`
3. Балансировщик ведет на ASG
4. ASG управляет EC2 инсансами на которых работает приложение `<my-service>`

### 2) aws account mc-project

![img](https://ah-public-pictures.hb.bizmrg.com/it-happens/kubed-cross-sync-2.jpeg)

Принимается решение перевезти приложение в kubernetes, для удобства под каждую команду создается свой aws аккаунт и свой k8s кластер:
1. В aws поднимается NLB балансировщик `<lb-my-project>`
2. Через target groups он смотрит на EC2 инстансы, на которых запущен pod с ingress controller-ом.
3. Попадая в pod ингресса, запрос через Ingress перенаправляется на pod-ы за `<my-service>` с помощью k8s service.

### 3) combine

![img](https://ah-public-pictures.hb.bizmrg.com/it-happens/kubed-cross-sync-3.jpeg)

r53 запись `<my-service>.<my-company>.io` начинает смотреть на CNAME `<lb-my-project>`, все работает, но SSL не терминируется.

Зона `<my-company>.io` слишком критична для бизнеса, и передавать в нее управление контроллерам типа external-dns, cert-manager не хочется.

В тоже время aws аккаунтов типа `mc-project` может быть много, как и кластеров k8s, вручную доставлять секрет с tls сертификатом не хочется.

### 4) Concept

![img](https://ah-public-pictures.hb.bizmrg.com/it-happens/kubed-cross-sync-4.png)

1. Создается специальный management aws аккаунт и k8s кластер.
2. В него каким-то образом доставляется секрет с tls сертификатом `*.<my-company>.io`
3. Специальный контроллер [kubed](https://github.com/kubeops/config-syncer) синхронизирует секрет `*.<my-company>.io` в другие кластеры k8s с помощью аннотаций.
4. Секрет `*.<my-company>.io` используется в Ingress, SSL траффик терминируется.

## Конфигурации

:::info

В последующих конфигурационных файлах роли для `mc-mgmt` будут называться `kubed-master`, а `mc-project-*` - `kubed-follower`

:::

### AWS IAM RBAC

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

:::info

На схеме `mc-mgmt` = `CI`, `mc-project` - `Target`

:::


![img](https://ah-public-pictures.hb.bizmrg.com/it-happens/kubed-cross-sync-aws-rbac.png)

Нужно сделать кросс-аккаунт aws iam rbac роли, для того, чтобы **kubed** из `mc-mgmt` мог управлять секретами в k8s кластерах других aws аккаунтов, в данном случае `mc-project`.

#### `mc-mgmt aka kubed-master`

<Tabs defaultValue="hcl">
<TabItem value="hcl" label="Terraform">

```hcl
locals {
  kubed_followers_arns = [
    for _, id in local.aws_accounts_map : "arn:aws:iam::${id}:role/kubed-follower"
  ]
}

module "iam_assumable_role_kubed_master" {
  source  = "terraform-aws-modules/iam/aws//modules/iam-assumable-role-with-oidc"
  version = "4.2.0"

  create_role = true
  role_name   = "kubed-master"

  provider_url = replace(local.cluster_oidc_issuer_url, "https://", "")

  role_policy_arns = [
    aws_iam_policy.kubed_master.arn,
    aws_iam_policy.kubed_eks.arn,
  ]

  oidc_fully_qualified_subjects = [
    "system:serviceaccount:kube-system:kubed"
  ]
}

data "aws_iam_policy_document" "kubed_master" {
  statement {
    sid    = "kubedMaster"
    effect = "Allow"
    actions = [
      "sts:AssumeRole",
    ]
    resources = local.kubed_followers_arns
  }
}

resource "aws_iam_policy" "kubed_master" {
  name   = "kubed-master"
  policy = data.aws_iam_policy_document.kubed_master.json
}

data "aws_iam_policy_document" "kubed_eks" {
  statement {
    sid    = "kubedEks"
    effect = "Allow"
    actions = [
      "eks:DescribeCluster",
      "eks:ListClusters"
    ]
    resources = ["*"]
  }
}

resource "aws_iam_policy" "kubed_eks" {
  name   = "kubed-eks"
  policy = data.aws_iam_policy_document.kubed_eks.json
}
```

</TabItem>
<TabItem value="trust" label="Trust policy">

```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Sid": "",
            "Effect": "Allow",
            "Principal": {
                "Federated": "arn:aws:iam:::<mc-mgmt_id>:oidc-provider/oidc.eks.<aws_region>.amazonaws.com/id/<mc-mgmt_oidc>"
            },
            "Action": "sts:AssumeRoleWithWebIdentity",
            "Condition": {
                "StringEquals": {
                    "oidc.eks.<aws_region>.amazonaws.com/id/<mc-mgmt_oidc>:sub": "system:serviceaccount:kube-system:kubed"
                }
            }
        }
    ]
}
```

</TabItem>
<TabItem value="policy-kubed-master" label="Policy kubed-master">

```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Sid": "kubedMaster",
            "Effect": "Allow",
            "Action": "sts:AssumeRole",
            "Resource": [
                "arn:aws:iam::<mc-project_id>:role/kubed-follower"
            ]
        }
    ]
}
```

</TabItem>
<TabItem value="policy-kubed-eks" label="Policy kubed-eks">

```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Sid": "kubedEks",
            "Effect": "Allow",
            "Action": [
                "eks:ListClusters",
                "eks:DescribeCluster"
            ],
            "Resource": "*"
        }
    ]
}
```

</TabItem>
</Tabs>

#### `mc-project` aka kubed-follower

<Tabs defaultValue="hcl">
<TabItem value="hcl" label="Terraform">

```hcl
locals {
  mc_mgmt_id = "<mc-mgmt_id>"
}

data "aws_iam_policy_document" "kubed_follower_assume" {
  statement {
    sid    = "kubedFollowerAssume"
    effect = "Allow"
    principals {
      identifiers = toset(["arn:aws:iam::${local.mc_mgmt_id}:role/kubed-master"])
      type        = "AWS"
    }
    actions = [
      "sts:AssumeRole",
    ]
  }
}

data "aws_iam_policy_document" "kubed_follower" {
  statement {
    sid    = "kubedEks"
    effect = "Allow"
    actions = [
      "eks:DescribeCluster",
      "eks:ListClusters"
    ]
    resources = ["*"]
  }
}


resource "aws_iam_policy" "kubed_follower" {
  name   = "kubed-follower"
  policy = data.aws_iam_policy_document.kubed_follower.json
}


resource "aws_iam_role" "kubed_follower" {
  name                = "kubed-follower"
  description         = "IAM role which allows kubed sync secrets from mc-mgmt to this account"
  assume_role_policy  = data.aws_iam_policy_document.kubed_follower_assume.json
  managed_policy_arns = [aws_iam_policy.kubed_follower.arn]
}
```

</TabItem>
<TabItem value="trust" label="Trust policy">

```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Sid": "kubedFollowerAssume",
            "Effect": "Allow",
            "Principal": {
                "AWS": "arn:aws:iam:::<mc-mgmt_id>:role/kubed-master"
            },
            "Action": "sts:AssumeRole"
        }
    ]
}
```

</TabItem>
<TabItem value="iam-policy" label="Policy kubed-eks">

```json
{
    "Statement": [
        {
            "Action": [
                "eks:ListClusters",
                "eks:DescribeCluster"
            ],
            "Effect": "Allow",
            "Resource": "*",
            "Sid": "kubedEks"
        }
    ],
    "Version": "2012-10-17"
}
```

</TabItem>
</Tabs>

#### ServiceAccount kubed

На **ServiceAccount** kubed-master нужно повесить аннотацию:

```yaml
annotations:
  eks.amazonaws.com/role-arn: arn:aws:iam::<mc-mgmt_id>:role/kubed-master
```

#### ConfgiMap aws-auth

<Tabs defaultValue="kubed-master">
<TabItem value="kubed-master" label="kubed master">

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: aws-auth
  namespace: kube-system
data:
  mapRoles: |
    - "groups":
      - "system:masters"
      "rolearn": "arn:aws:iam::<mc-mgmt_id>:role/kubed-master"
      "username": ""
      ...
```

</TabItem>
<TabItem value="kubed-follower" label="kubed follower">

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: aws-auth
  namespace: kube-system
data:
  mapRoles: |
    - "groups":
      - "system:masters"
      "rolearn": "arn:aws:iam::<mc-project_id>:role/kubed-follower"
      "username": ""
      ...
```


</TabItem>
</Tabs>

### Docker image

Образ от разработчиков scratch, в нем есть только бинарник kubed, нам же нужны утилиты aws для генерирования kubeconfig.

```Dockerfile
FROM appscode/kubed:v0.13.2 as downloader

FROM alpine:3.17

COPY --from=downloader /kubed /usr/bin/kubed

RUN apk add --no-cache \
  curl~=7.86 \
  py3-pip~=22.3 \
  && pip install --no-cache-dir \
  awscli~=1.27 \
  && curl -Lo aws-iam-authenticator https://github.com/kubernetes-sigs/aws-iam-authenticator/releases/download/v0.5.9/aws-iam-authenticator_0.5.9_linux_amd64 \
  && chmod +x aws-iam-authenticator \
  && mv aws-iam-authenticator /usr/bin/

RUN addgroup --gid 1950 app \
  && addgroup --gid 1000 app \
  && adduser \
  --uid 1000 \
  --home /home/app \
  --shell /bin/ash \
  --ingroup app \
  --disabled-password \
  app \
  && addgroup app app

USER 1000
WORKDIR /home/app

ENTRYPOINT ["/usr/bin/kubed"]
```

### K8s controller

В mc-mgmt кластере так же работает обычный интанс kubed-а, установленный [helm чартом](https://github.com/kubeops/config-syncer/tree/master/charts/kubed), из него мы и берем все необходимые k8s RBAC-и.

:::danger

Этот способ **деструктивен**, неверная конфигурация kubed-master может реверсировать синхронизацию секретов между namespace-ами. Рекомендация держать специальный кластер для kubed-master

:::

<Tabs defaultValue="cm">
<TabItem value="cm" label="ConfigMap">

```yaml
---
apiVersion: v1
kind: ConfigMap
metadata:
  name: kubed-master-aws
  namespace: kube-system
data:
  credentials: |-
    [mc-mgmt]
    role_arn = arn:aws:iam::<mc-mgmt_id>:role/kubed-master
    web_identity_token_file = /var/run/secrets/eks.amazonaws.com/serviceaccount/token
    [mc-project]
    role_arn = arn:aws:iam::<mc-project_id>:role/kubed-follower
    source_profile = mc-mgmt
    role_session_name = mc-project
  generate-kubeconfig.sh: |-
    #!/bin/bash
    set -eux

    aws eks update-kubeconfig --name mc-project-k8s --alias mc-project-k8s --profile mc-project

    # NOTE: mc-mgmt-k8s should the last due to current-context
    aws eks update-kubeconfig --name mc-mgmt-k8s --alias mc-mgmt-k8s --profile mc-mgmt
```

</TabItem>

<TabItem value="deploy" label="Deployment">

```yaml
---

apiVersion: apps/v1
kind: Deployment
metadata:
  name: kubed-master
  namespace: kube-system
  labels:
    app.kubernetes.io/name: kubed-master
    app.kubernetes.io/instance: kubed-master
    app.kubernetes.io/version: "v0.13.2"
spec:
  replicas: 1
  selector:
    matchLabels:
      app.kubernetes.io/name: kubed-master
      app.kubernetes.io/instance: kubed-master
  template:
    metadata:
      labels:
        app.kubernetes.io/name: kubed-master
        app.kubernetes.io/instance: kubed-master
    spec:
      serviceAccountName: kubed
      # NOTE: kubeconfig-generator
      initContainers:
        - name: kubeconfig-generator
          image: docker.io/my-company/kubed:v0.13.2
          volumeMounts:
            - name: kubeconfig
              mountPath: /srv/kubed
            - name: aws-config
              mountPath: /home/app/.aws
            - name: kubed-master-aws
              mountPath: /home/app/scripts
          command:
            - sh
            - -c
            - |
              mkdir -p /home/app/.aws &&
              cp /home/app/scripts/credentials /home/app/.aws &&
              sh /home/app/scripts/generate-kubeconfig.sh &&
              cp /home/app/.kube/config /srv/kubed/kubeconfig

      containers:
        - name: kubed-master
          image: docker.io/my-company/kubed:v0.13.2
          args:
            - run
            - --v=3
            - --secure-port=8443
            - --audit-log-path=-
            - --tls-cert-file=/var/serving-cert/tls.crt
            - --tls-private-key-file=/var/serving-cert/tls.key
            - --use-kubeapiserver-fqdn-for-aks=true
            - --enable-analytics=false
            - --cluster-name=mc-mgmt
            - --kubeconfig-file=/srv/kubed/kubeconfig
            - --config-source-namespace=prod
          ports:
            - containerPort: 8443
          resources: {}
          volumeMounts:
            - name: kubeconfig
              mountPath: /srv/kubed
            - name: aws-config
              mountPath: /home/app/.aws
            - name: scratch
              mountPath: /tmp
            - name: serving-cert
              mountPath: /var/serving-cert
      volumes:
        # NOTE: we'd like to generate kubeconfig during initContainer
        - name: kubeconfig
          emptyDir: {}
          # secret:
          #   secretName: kubed # NOTE: contains data.kubeconfig
        - name: aws-config
          emptyDir: {}
        - name: kubed-master-aws
          configMap:
            name: kubed-master-aws
            defaultMode: 0550
        - name: scratch
          emptyDir: {}
        - name: serving-cert
          secret:
            defaultMode: 420
            secretName: kubed-apiserver-cert
      securityContext:
        fsGroup: 1000
```

</TabItem>
</Tabs>



## Синхронизация конфигураций

```yaml
---

apiVersion: v1
kind: ConfigMap
metadata:
  name: cross-acc-sync-demo
  namespace: prod
  annotations:
    kubed.appscode.com/sync-contexts: "mc-project-k8s"
data:
  foo: bar
  spam: eggs
```

## Нюансы работы

:::info

конфигурация: это ConfigMap, Secret

:::

- Синхронизация возможно только из namespace-а указанного во флагах контроллера в namespace с таким же названием в follower кластерах. При это annotations и labels на конфигурациях в follower кластерах не сохраняется.
- Поводом для синхронизации конфигураций является: перезапуск pod-а контроллера, обновление `.data` конфигурации. Т.е. если конфигурация будет удалена в follower кластере, она не синхронизуется автоматом.
- Удаление конфигурации в master аккаунте, удалит конфигурацию во всех follower-ах.
- В случае, если в follower кластере есть свой kubed для синхронизации между namespace-ами, то можно добавить annotation-ию вручную и конфигурация разбежится по namespace-ам. Причем обновление `.data` в master кластере синхронизирует секрет в follower, но не перетрет эту аннотацию.

Добавляем аннотацию в follower кластере
```shell
kubectl --context mc-project annotate cm cross-acc-sync-demo "kubed.appscode.com/sync=sync/kubed-master=true"
```

Добавляем label на другой namespace в follower кластере, чтобы местный kubed засинхронизировал cm между namespace-ами.

```yaml
---

kind: Namespace
apiVersion: v1
metadata:
  name: env-ahorbach
  labels:
    name: env-ahorbach
    sync/kubed-master: "true"
```

## Ссылки

- [Imran Hayder: Adding cross-account access to EKS](https://dev.to/hayderimran7/adding-cross-account-access-to-eks-5ebh)
- [AWS: Enabling cross-account access to Amazon EKS cluster resources](https://aws.amazon.com/blogs/containers/enabling-cross-account-access-to-amazon-eks-cluster-resources/)
- [kubed: Synchronize Configuration across Clusters](https://appscode.com/products/kubed/v0.12.0/guides/config-syncer/inter-cluster/)
- [jdepp: KS cross-cluster and cross-namespace syncing issue.](https://github.com/kubeops/config-syncer/issues/457)
