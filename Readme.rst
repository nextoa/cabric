Fabez
==========

简单,敏捷的发布系统. 致力于为Github用户提供更简单的服务

Currently, this is a unstable version realease.


TODO
============
- 异步方式实现发布流程
- 构造watchdog,防止用于撰写了不当的fab脚本导致进程永久性挂起






关于安全性
============
可以参考下 https://www.digitalocean.com/community/tutorials/how-to-create-a-ssl-certificate-on-nginx-for-centos-6

- 生成证书
sudo openssl genrsa -des3 -out server.key 1024

sudo openssl req -new -key server.key -out server.csr

sudo cp server.key server.key.org

sudo openssl rsa -in server.key.org -out server.key

sudo openssl x509 -req -days 365 -in server.csr -signkey server.key -out server.crt





