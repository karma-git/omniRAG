---
title: "debug helm chart"
tags:
  - k8s
  - helm
  - python
  - helm
---


# debug helm chart

Приемы для локальной отладки helm chart-ов

## $ helm template

Если перейти в локально скачанный чарт и выполнить команду, то можно получить итоговые манифесты

```shell
helm template MyReleaseName ./ -f values.yaml --output-dir ./render --debug
```

## merged values

Как известно, helm engine берет values которые вы передаете в release и очень хитро merge-ит их со стандартными values-ами chart-а.

За счет этого сильно увеличивается DRY, т.к. в релизе можно переопределять только нужные параметры. Но что, если нужно увидеть получившиеся values-ы?

Можно сделать с помощью такого [сниппета](https://github.com/karma-git/kb/tree/master/swe/python/helm-values-merge):

```python
# pip install deepmerge pyaml
from copy import deepcopy

import yaml
from deepmerge import Merger

m = Merger(
    # ref: https://deepmerge.readthedocs.io/en/latest/strategies.html#builtin-strategies
    [
        (list, ["override"]),
        (dict, ["merge"]),
        (set, ["union"])
    ],
    # fallback
    ["use_existing"],
    # conflict
    ["use_existing"]
)

def main() -> None:
    with open("chart.values.yaml") as y:
        chart = yaml.safe_load(y)
    with open("release.values.yaml") as y:
        release = yaml.safe_load(y)

    # save copy of release values
    release_values = deepcopy(release)

    # all that we want is set, except we got chart Lists instead of Release Lists
    m.merge(release, chart)
    # return release lists
    m.merge(release, release_values)

    with open("merged.values.yaml", "w") as y:
        yaml.dump(release, y)

if __name__ == "__main__":
    main()
```
