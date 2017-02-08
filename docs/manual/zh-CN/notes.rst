一些实现策略细节备注
===================================


pip install -r requirements* 的顺序是什么
---------------------------------------------

考虑到线上的高可用性，我们不会对包进行升级安装

安装 requirements-zip.txt
安装 requirements-static.txt
安装 requirements-private-static.txt

一次性安装 requirements.txt
一次性安装 requirements-private.txt




关于证书生成的路径
---------------------------------------------

由于certbot的证书是支持多个域名的，所以证书生成后，存放名称会存在一点迷惑性

certbot证书会根据第一次创建时的最后一个证书来生成证书




