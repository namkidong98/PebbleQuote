1. EC2 서버 OS 확인
```bash
cat /etc/os-release
# NAME="Amazon Linux"
# Amazon Linux는 Centos 및 RHEL 기반으로 만들어진 리눅스 배포판이라고 한다
# 그래서 패키지 관리 명령어로 Ubuntu에서 사용하는 apt가 안 먹히고 주로 yum을 쓴다
# 파이썬 버전도 3.9가 default라 진짜 이것저것 손 많이 가는 쓰레기 os인거 같다.... AWS가 싫어졌다....
```

<br>

2. pem키 없이 비밀번호로 접속할 수 있도록 변경
```bash
sudo -i # root 사용자로 전환
passwd ec2-user # 해당 유저의 비밀번호를 부여
nano /etc/ssh/sshd_config # SSH 설정 파일 편집
# PasswordAuthentication yes
# ChallengeResponseAuthentication no
# UsePAM yes
systemctl restart sshd
```

<br>

3. 서버 기본 설치
```bash
sudo yum update -y # 시스템 업데이트
sudo yum groupinstall -y "Development Tools" 
sudo yum install -y readline-devel zlib-devel libicu-devel sqlite-devel postgresql-devel
sudo yum install -y python3-pip python3-devel gcc openssl-devel bzip2-devel libffi-devel wget # 필수 패키지 설치
sudo yum install -y python3-virtualenv # 가상환경 패키지
```

<br>

4. 파이썬 3.11.7 버전 설치
```bash
cd /usr/src
sudo wget https://www.python.org/ftp/python/3.11.7/Python-3.11.7.tgz # 다운로드
sudo tar xzf Python-3.11.7.tgz # 압축해제
cd Python-3.11.7
sudo ./configure --enable-optimizations # 컴파일 전 컴파일 옵션 지정
sudo make altinstall # Makefile을 읽고 컴파일 및 설치
/usr/local/bin/python3.11 --version # 설치 확인

```

<br>

5. PostgreSQL 16.3 버전 설치
```bash
sudo wget https://ftp.postgresql.org/pub/source/v16.3/postgresql-16.3.tar.gz
sudo tar xzf postgresql-16.3.tar.gz
cd postgresql-16.3
sudo ./configure
sudo make
sudo make install
/usr/local/pgsql/bin/psql --version # 설치되었는지 확인
```

<br>

6. PostgreSQL 초기 설정
```bash
sudo useradd postgres # postgres 관리할 유저를 따로 생성
sudo mkdir /usr/local/pgsql/data
sudo chown postgres /usr/local/pgsql/data
sudo -i -u postgres # postgres 유저로 변경
/usr/local/pgsql/bin/initdb -D /usr/local/pgsql/data # 데이터베이스 초기화
/usr/local/pgsql/bin/pg_ctl start -D /usr/local/pgsql/data -l /usr/local/pgsql/data/logfile # Postgresql DB 시작

/usr/local/pgsql/bin/psql -U postgres # DB 접속
ALTER USER postgres WITH PASSWORD '1234'; # 비밀번호 수정
\q # DB 접속 종료

/usr/local/pgsql/bin/psql -U postgres -W # 비밀번호 받는 W 옵션으로 접속
create database quote_db; # Django 서버를 위해 quote_db 생성
\q # DB 접속 종료

exit # ec2-user로 다시 전환
```

<br>

7. PostgreSQL 서비스 설정
```bash
sudo nano /etc/systemd/system/postgresql.service
# [Unit]
# Description=PostgreSQL database server
# After=network.target
# 
# [Service]
# Type=forking
# User=postgres
# ExecStart=/usr/local/pgsql/bin/pg_ctl start -D /usr/local/pgsql/data -l # /usr/local/pgsql/data/logfile
# ExecStop=/usr/local/pgsql/bin/pg_ctl stop -D /usr/local/pgsql/data
# ExecReload=/usr/local/pgsql/bin/pg_ctl reload -D /usr/local/pgsql/data
# PIDFile=/usr/local/pgsql/data/postmaster.pid
# Restart=always
# 
# [Install]
# WantedBy=multi-user.target

sudo systemctl daemon-reload
sudo pkill postgres # 이미 실행해둔 서버를 일단 닫고
sudo systemctl start postgresql # postgresql 서비스 시작
sudo systemctl enable postgresql # 자동 시작 설정
```

<br>

8. PostgreSQL 설정 파일 수정
```bash
sudo nano /usr/local/pgsql/data/pg_hba.conf
# 맨 아래에 다음 줄 추가
# Allow all IP addresses to connect using md5 (password authentication)
# host    all             all             0.0.0.0/0               md5
# host    all             all             ::/0                    md5
sudo systemctl restart postgresql

sudo nano /usr/local/pgsql/data/postgresql.conf # 
# listen_addresses = '*'
sudo systemctl restart postgresql

/usr/local/pgsql/bin/psql -U postgres -W # 이제 이 명령어로 접속하면 됨
```

<br>

9. Timezone 설정
```bash
timedatectl                              # 현재 VM의 Timezone 확인
sudo timedatectl set-timezone Asia/Seoul # 한국 Timezone으로 변경
timedatectl                              # Timezone 변경 확인
```

<br>

10. Chromadb 설정
```bash
cd /home/ec2-user/
mkdir chroma
cd chroma
python3.11 -m venv chromadb-env
source chromadb-env/bin/activate
pip install chromadb==0.4.22
deactivate

sudo nano /etc/systemd/system/chromadb.service
# [Unit]
# Description=ChromaDB Service
# After=network.target
# 
# [Service]
# User=ec2-user
# WorkingDirectory=/home/ec2-user/chromadb-env
# ExecStart=/home/ec2-user/chromadb-env/bin/chroma run --host 0.0.0.0 --port 8001 --path ./data
# Restart=always
# 
# [Install]
# WantedBy=multi-user.target

sudo systemctl daemon-reload
sudo systemctl start chromadb
sudo systemctl enable chomradb
```

<br>

11. Django 서버 설치 및 설정
```bash
cd /home/ec2-user/
mkdir backend
cd backend
# FileZilla로 파일 전송
/usr/local/bin/python3.11 -m venv django-env     # 가상환경 설치
source venv/bin/activate   # 가상환경 활성화
pip install --upgrade pip # 가상환경 내 pip 업그레이드
pip install -r requirements.txt   # 의존성 설치
```

<br>

12. 리버스 프록시 설정(Nginx가 수신하는 80번 포트(http) 인바운드 트래픽을 내부의 8000번 포트에서 실행 중인 Django 앱으로 포워딩)
```bash
sudo systemctl status nginx # 이미 설치되어 있다고 하니 확인만

# 디렉토리 생성
sudo mkdir -p /etc/nginx/sites-available
sudo mkdir -p /etc/nginx/sites-enabled

sudo nano /etc/nginx/sites-available/django_server # 설정 파일 작성
# server {
#         listen 80;
#         server_name 15.164.27.255;
# 
#         location / {
#                 proxy_pass http://127.0.0.1:8000;
#                 proxy_set_header Host $host;
#                 proxy_set_header X-Real-IP $remote_addr;
#                 proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
#                 proxy_set_header X-Forwarded-Proto $scheme;
#         }
# }
sudo ln -s /etc/nginx/sites-available/django_server /etc/nginx/sites-enabled/ # 설정 파일 활성화
sudo nano /etc/nginx/nginx.conf # 기존 Nginx 설정 파일 수정
# include /etc/nginx/sites-enabled/*; # 해당 줄 추가하기
(http { 내부에 "include /etc/nginx/conf.d/*.conf;" 아래줄에 추가)
sudo nginx -t # 테스트
sudo systemctl restart nginx # 재시작
```

<br>

13. Django 실행 확인(돌아가는지만 체크)
```bash
# makemigrations & migrate를 마친 상황에서
# settings.py의 ALLOWED_HOSTS = ['*'] 로 수정
# .env의 CHROMA_HOST="127.0.0.1"로 수정
source django-env/bin/activate
python manage.py runserver
# 15.164.27.255/accounts/register/ 로 유저 명단 확인 가능 -> 잘 돌아간다
```

<br>

14. Django 프로덕션용 gunicorn 배포 
```bash
source django-env/bin/activate
pip install gunicorn
gunicorn --workers 4 --bind 0.0.0.0:8000 config.wsgi:application # 돌아가는지 확인
# (static 로드하는데 문제 생기는 꼴을 보니 괜히 했다가 문제만 많아질 삘, 잠정 중단)
```

<br>

15. Django 서비스 자동화 설정
```bash
sudo nano /etc/systemd/system/django.service # 서비스 파일 작성
# [Unit]
# Description=Django Server
# After=network.target
# 
# [Service]
# User=ec2-user
# Group=ec2-user
# WorkingDirectory=/home/ec2-user/backend/django-env
# ExecStart=/home/ec2-user/backend/django-env/bin/python /home/ec2-user/backend/manage.py runserver 0.0.0.0:8000
# Restart=always
# 
# [Install]
# WantedBy=multi-user.target

sudo systemctl daemon-reload
sudo systemctl start django # 장고 서비스 실행
sudo systemctl enable django # 자동화 등록
sudo systemctl status django # 잘 되는지 확인
```

<br>

16. 불필요한 (enabled된)서비스 비활성화
```bash
sudo systemctl list-units --type=service --state=running # 활성화된 서비스 목록 확인
sudo systemctl disable mariadb # 기존에 서버 넘겨줄 때 켜져있던 mariadb 제거하기
sudo systemctl stop mariadb # 기존에 실행되던 것도 중단
sudo systemctl status mariadb # inactive, disabled인지 확인
```

<br>

17. Fail2Ban 설정 (무작위 스캔 공격 방지)
```
# Amazon Linux에서는 이것도 지원 안한다고 해서 수동 설치가 필요하다해서 그냥 포기
```