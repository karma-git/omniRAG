---
title: Helm vs Python validation
description: Я ненавижу helm
slug: helm-vs-python
authors: [a.horbach]
tags: [helm, python, pydantic, pytest, karpenter]
image: https://i.imgur.com/mErPwqL.png
hide_table_of_contents: false

---

# Описание

Решали с коллегами задачу по генерации манифестов **Provisioner** в цикле, при таком создании есть один деструктивный момент - нужно выбрать Container Runtime Interface (CRI), иначе  `provisioner.spec.kubeletConfiguration.containerRuntime` в манифесте **Provisioner** в паре с **AWSNodeTemplate** karpenter по дефолту выставят нам `containerd` ([подтверждение в тесте](https://github.com/aws/karpenter/blob/7241f43569d6878056f3251667b4689684071401/pkg/cloudprovider/launchtemplate_test.go#L894))

Собрали ряд требований:
- CRI не указан в провиженере, значит выбираем дефолтный для нас (в нашем случае dockerd)
- CRI указан в провиженере, выбираем его
- CRI не указан в провиженере, но в `provisioner.spec.kubeletConfiguration` есть другие параметры

Получился следующий код валидации:

## helm

```yaml
  # Kubelet
  # If Provisioner.kubeletConfiguration is not empty
  {{- if .kubeletConfiguration }}
  kubeletConfiguration:
    # If containerRuntime has been configured in Provisioner.kubeletConfiguration
    {{- if hasKey .kubeletConfiguration "containerRuntime" -}}
      {{- toYaml .kubeletConfiguration | nindent 4 }}
    # ElseIf containerRuntime has not been configured in Provisioner.kubeletConfiguration
    {{- else }}
      # Pick default CRI from karpenter.default.kubeletConfiguration and add it to current .kubeletConfiguration
      {{- $CRI := dict "containerRuntime" $.Values.karpenter.default.kubeletConfiguration.containerRuntime -}}
      {{- $kubeletConfiguration := merge $CRI .kubeletConfiguration }}
      {{- toYaml $kubeletConfiguration | nindent 4 }}
    {{- end }}
  # ElseIf Provisioner.kubeletConfiguration is empty
  {{- else }}
  kubeletConfiguration:
      {{- toYaml $.Values.karpenter.default.kubeletConfiguration | nindent 4 }}
  {{- end }}
```

<details>
<summary>Тесты</summary>

Test cases:

- 1) CRI не указан в провиженере
values.yml
```yaml
karpenter:
  payload:
    ahorbach:
      foo: bar
```

result:
```yaml
spec:
  # Kubelet
  # If Provisioner.kubeletConfiguration is not empty
  kubeletConfiguration:
    containerRuntime: dockerd
```
- 2) CRI указан в провиженере

values.yml
```yaml
karpenter:
  payload:
    ahorbach:
      kubeletConfiguration:
        bar: baz
        containerRuntime: rocket
```

result:
```yaml
spec:
  # Kubelet
  # If Provisioner.kubeletConfiguration is not empty
  kubeletConfiguration:
    # If containerRuntime has been configured in Provisioner.kubeletConfiguration
    bar: baz
    containerRuntime: rocket
    # ElseIf containerRuntime has not been configured in Provisioner.kubeletConfiguration
  # ElseIf Provisioner.kubeletConfiguration is empty
```

- 3) CRI не указан в провиженере, но есть конфиг

values.yml
```yaml
  payload:
    ahorbach:
      kubeletConfiguration:
        spam: eggs
```

result:
```yaml
spec:
  # Kubelet
  # If Provisioner.kubeletConfiguration is not empty
  kubeletConfiguration:
    # If containerRuntime has been configured in Provisioner.kubeletConfiguration
      # Pick default CRI from karpenter.default.kubeletConfiguration and add it to current .kubeletConfiguration
    containerRuntime: dockerd
    spam: eggs
```

</details>

## python

```python
from pydantic import BaseModel, validator

DEFAULT_CRI = {"containerRuntime": "dockerd"}

class karpenterPayloadProvisioner(BaseModel):
  name: str
  kubelet_configuration: dict = DEFAULT_CRI

  @validator('kubelet_configuration')
  def kubelet_container_runtime(cls, v):
    cri = v.get("containerRuntime")
    # option two - Mutating
    if cri not in ["dockerd", "containerd"]:
      v.update(DEFAULT_CRI)
    return v
```

<details>
<summary>Тесты</summary>

```python
import typing as t

import pytest

from karpenter import karpenterPayloadProvisioner

# without selected CRI in Provisioner
case1 = ("foo", {}, "dockerd")

# with containerd as a CRI for Provisioner

case2 = ("bar", {"kubeReserved": "testMe", "containerRuntime": "containerd"}, "containerd")

# with typo in CRI for Provisioner
case3 = ("baz", {"kubeReserved": "testMe", "containerRuntime": "qwerty"}, "dockerd")

test_cases = [
    case1,
    case2,
    case3,
]

@pytest.mark.parametrize("name, kubelet_configuration, expected_CRI", test_cases)
def test_cri_provisioner(name: str, kubelet_configuration: t.Optional[dict], expected_CRI: str):

    provisioner = karpenterPayloadProvisioner(name=name, kubelet_configuration=kubelet_configuration)
    assert provisioner.kubelet_configuration["containerRuntime"] == expected_CRI

```

```shell
pytest .
=========================================================== test session starts ============================================================
platform darwin -- Python 3.10.0, pytest-6.2.5, py-1.11.0, pluggy-1.0.0
rootdir: /Users/a.horbach/repository-self/python-monorepo/pydantic-karpenter
plugins: django-4.4.0, cov-3.0.0
collected 3 items

test_karpenter.py ...                                                                                                                [100%]

============================================================ 3 passed in 0.08s =============================================================
```

</details>

## Links

- [python code](https://github.com/karma-git/Python-Playground/tree/master/pydantic-karpenter)
- [pydantic](https://github.com/pydantic/pydantic)
- [pytest](https://github.com/pytest-dev/pytest)
- [karpenter](https://github.com/aws/karpenter)
- [pydantic digitalize video](https://www.youtube.com/watch?v=dOO3GmX6ukU)
