---
title: "14 - Fix Issue with VolumeMounts in Kubernetes"
tags:
  - kodekloud-engineer-kubernetes
---

## Task

We deployed a Nginx and PHP-FPM based setup on Kubernetes cluster last week and it had been working fine so far. This morning one of the team members made a change somewhere which caused some issues, and it stopped working. Please look into the issue and fix it:



The pod name is nginx-phpfpm and configmap name is nginx-config. Figure out the issue and fix the same.


Once issue is fixed, copy /home/thor/index.php file from the jump host to the nginx-container under nginx document root and you should be able to access the website using Website button on top bar.


Note: The kubectl utility on jump_host has been configured to work with the kubernetes cluster.


## Solution


check cm, and find that nginx root is `/var/www/html`

```shell
thor@jump_host ~$ k get cm nginx-config -o yaml
apiVersion: v1
data:
  nginx.conf: |
    events {
    }
    http {
      server {
        listen 8099 default_server;
        listen [::]:8099 default_server;

        # Set nginx to serve files from the shared volume!
        root /var/www/html;
        index  index.html index.htm index.php;
        server_name _;
        location / {
          try_files $uri $uri/ =404;
        }
        location ~ \.php$ {
          include fastcgi_params;
          fastcgi_param REQUEST_METHOD $request_method;
          fastcgi_param SCRIPT_FILENAME $document_root$fastcgi_script_name;
          fastcgi_pass 127.0.0.1:9000;
        }
      }
    }
kind: ConfigMap
metadata:
  name: nginx-config
  namespace: default
```

If we check pod, we'll find that Pod config assumes that nginx root is `/usr/share/nginx/html`
```shell
thor@jump_host ~$ kubectl get pod nginx-phpfpm -o yaml  > /tmp/nginx.yaml
thor@jump_host ~$ cat /tmp/nginx.yaml | grep /usr/share/nginx/html
      {"apiVersion":"v1","kind":"Pod","metadata":{"annotations":{},"labels":{"app":"php-app"},"name":"nginx-phpfpm","namespace":"default"},"spec":{"containers":[{"image":"php:7.2-fpm-alpine","name":"php-fpm-container","volumeMounts":[{"mountPath":"/var/www/html","name":"shared-files"}]},{"image":"nginx:latest","name":"nginx-container","volumeMounts":[{"mountPath":"/usr/share/nginx/html","name":"shared-files"},{"mountPath":"/etc/nginx/nginx.conf","name":"nginx-config-volume","subPath":"nginx.conf"}]}],"volumes":[{"emptyDir":{},"name":"shared-files"},{"configMap":{"name":"nginx-config"},"name":"nginx-config-volume"}]}}
    - mountPath: /usr/share/nginx/html
```
Fix it, replace `/usr/share/nginx/html` to `/var/www/html` and recreate the Pod
```shell
thor@jump_host ~$ vi /tmp/nginx.yaml
thor@jump_host ~$ kubectl replace -f /tmp/nginx.yaml --force
pod "nginx-phpfpm" delete
```

Copy php script and test web service
```shell
thor@jump_host ~$ kubectl cp  /home/thor/index.php  nginx-phpfpm:/var/www/html -c nginx-container
thor@jump_host ~$ kubectl exec -it nginx-phpfpm -c nginx-container  -- curl -I  http://localhost:8099
HTTP/1.1 200 OK
Server: nginx/1.25.2
Date: Thu, 14 Sep 2023 05:46:42 GMT
Content-Type: text/html; charset=UTF-8
Connection: keep-alive
X-Powered-By: PHP/7.2.34
```
