# Linux diagnostics (WSL2)

## OS / kernel

```
PS D:\Interviews\Paysys\minipay-platform> wsl -d Ubuntu
huzaifa@H:/mnt/d/Interviews/Paysys/minipay-platform$ uname -a
Linux H 6.6.87.2-microsoft-standard-WSL2 #1 SMP PREEMPT_DYNAMIC Thu Jun  5 18:30:46 UTC 2025 x86_64 GNU/Linux
huzaifa@H:/mnt/d/Interviews/Paysys/minipay-platform$ cat /etc/os-release | head -3
PRETTY_NAME="Ubuntu 26.04.1 LTS"
NAME="Ubuntu"
VERSION_ID="26.04"
```

## CPU and load

```
huzaifa@H:/mnt/d/Interviews/Paysys/minipay-platform$ lscpu | egrep 'Model name|^CPU\(s\)'
CPU(s):                               8
Model name:                           Intel(R) Core(TM) i7-10610U CPU @ 1.80GHz
huzaifa@H:/mnt/d/Interviews/Paysys/minipay-platform$ nproc
8
huzaifa@H:/mnt/d/Interviews/Paysys/minipay-platform$ uptime
 16:08:27 up  2:10,  2 users,  load average: 0.37, 0.47, 0.49
```

## Memory

```
huzaifa@H:/mnt/d/Interviews/Paysys/minipay-platform$ free -h
               total        used        free      shared  buff/cache   available
Mem:            15Gi       1.8Gi        11Gi        68Mi       2.2Gi        13Gi
Swap:          4.0Gi          0B       4.0Gi
```

## Disk

```
huzaifa@H:/mnt/d/Interviews/Paysys/minipay-platform$ df -hT /
du -xsh /var/lib/docker/* 2>/dev/null | sort -h | tail -5
Filesystem     Type  Size  Used Avail Use% Mounted on
/dev/sdf       ext4 1007G  1.4G  955G   1% /
```

## Listening ports

```
huzaifa@H:/mnt/d/Interviews/Paysys/minipay-platform$ ss -tulpn | egrep '8000|8080|5432'
tcp   LISTEN 0      4096                *:8080             *:*
```

## DNS and API readiness

```
huzaifa@H:/mnt/d/Interviews/Paysys/minipay-platform$ getent hosts github.com
curl -sI http://localhost:8080/ready | head -3
20.207.73.82    github.com
HTTP/1.1 405 Method Not Allowed
Allow: GET
Content-Length: 31
```

## Kubernetes (Postgres service)

```
huzaifa@H:/mnt/d/Interviews/Paysys/minipay-platform$ kubectl -n minipay get svc minipay-db
NAME         TYPE        CLUSTER-IP      EXTERNAL-IP   PORT(S)    AGE
minipay-db   ClusterIP   10.43.240.252   <none>        5432/TCP   14h
```
