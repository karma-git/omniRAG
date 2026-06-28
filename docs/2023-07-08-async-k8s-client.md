---
title: "async kubernetes клиент для python"
tags:
  - python
  - kubernetes
date: 2023-07-08
---

# async kubernetes клиент для python


## Проблематика

При необходимости выполнить kubectl команду на большом числе кластеров это делается крайне медленно в цикле for, пример:

```shell
for ctx in $(kubectl config view | yq '.contexts.[].name'); 
	do echo $ctx; 
	kubectl --context $ctx get cm aws-auth -n kube-system -o yaml | yq e '.data.mapUsers' - | yq -; 
done
```

## Решение

Можно использовать асинхронный клиент на python:

```shell
pip3 install kubernetes_asyncio
```

Создадим класс, который будет запускать задачи и дожидаться их отработки:
```python
import asyncio
from kubernetes_asyncio import client, config
from kubernetes_asyncio.client.api_client import ApiClient

import typing as t


class k8sAsyncTask:
    def __init__(self, contexts: list, task: t.Callable):
        self._ctxs = contexts
        self._task = task

    async def _task_runner(self, ctx):
        try:
            # Загрузка конфигурации кластера
            await config.load_kube_config(context=ctx)

            # use the context manager to close http sessions automatically
            async with ApiClient() as api:
                result = await self._task(api)
                return ctx, result

        except Exception as e:
            # Обработка ошибок, если необходимо
            print(f"Error in cluster {ctx}: {str(e)}")
            return ctx, None

    async def tasks_results(self):
        tasks = []

        for ctx in self._ctxs:
            task = asyncio.create_task(self._task_runner(ctx))
            tasks.append(task)

        # Ожидание завершения всех задач
        completed_tasks = await asyncio.gather(*tasks)
        # Преобразуем списки с результатами в словари
        zipped = dict(zip(self._ctxs, completed_tasks))
        result = {k: zipped[k][1] for k in zipped}

        return result
```

Создадим задачу - просмотр ConfigMap с пользователями aws:

```python
import yaml


async def k8s_get_aws_auth(api):
    v1 = client.CoreV1Api(api)
    result = await v1.read_namespaced_config_map(name="aws-auth", namespace="kube-system")
    users = yaml.safe_load(result.data["mapUsers"])
    users_groups = [{"username": user["username"], "group": user["groups"]} for user in users]
    return users_groups
```

запуск задач и ожидание результата:

```python
CLUSTERS = ["dev", "prod"]


async def main():
    k = k8sAsyncTask(CLUSTERS, k8s_get_aws_auth)
    r = await k.tasks_results()
    return r


if __name__ == "__main__":
    r = asyncio.run(main())
    print(r)

```

Done

## Вывод
- при условии большого числа кластеров, adhoc задачи можно выполнять быстрее

## Cсылки
- [kubernetes_asyncio](https://github.com/tomplus/kubernetes_asyncio)(https://github.com/tomplus/kubernetes_asyncio)

