# Pebble
<img width="800" alt="1" src="https://github.com/user-attachments/assets/b9215b93-303b-4766-b4b0-f10d3260dd08">

- 서비스 컨셉
	- 바다는 우리의 답답함을 풀어주는 장소이다. 
	- 바다를 가면 우리를 반겨주는 모래 위에 작은 Pebble(조약돌)처럼,
	- 우리의 서비스가 현대인들이 명언을 추천 받고 자신만의 Pebble(명언)을 기록하고 공유하며 쉬어갈 수 있는 공간이 되길 바란다
	- 부정적인 마음들은 바다에 흘려보내고 Pebble을 쌓아가자.
- 기능 소개
	- 사용자의 한풀이를 위로해줄 수 있는 명언 추천
 	- 나만의 개성을 담은 명언을 게시 및 공유
  	- 좋아요, 댓글, 팔로우를 통한 사용자들의 상호작용

<br>

## 프로젝트 설명
- 프로젝트명 : Pebble
- 프로젝트 목표 : 현대인의 정신 건강 문제를 해결하고자 사용자의 한풀이를 위로해줄 수 있는 명언을 추천해주는 서비스
- 프로젝트 기간 : 2024.07.04 ~ 2024.08.06
- 프로젝트 인원 : 김경우, 나현진, 남기동, 안연아, 이형빈, 정혜나

<br>

## 담당 업무
1. Backend
	- Django 프레임워크를 활용한 RESTful API 설계 및 구현
	- 초기 데이터셋(명언 100개) 구축 및 데이터 마이그레이션 파이프라인 개발
2. Cloud
	- AWS EC2를 활용한 서버 환경 구축 및 관리
 	- Django, PostgreSQL, ChromaDB 통합 환경 구축
 	- Nginx를 활용한 웹 트래픽 관리 및 DNS를 통한 HTTPS 통신 구현
	- Systemd 서비스 유닛 파일을 이용한 서비스 자동화 및 Cron을 통한 작업 스케줄링
3. Vector Search
	- ChromaDB와 Upstage Solar-embedding을 이용한 명언 텍스트 임베딩
 	- ChromaDB의 vector search를 이용해 사용자 입력에 맞는 명언 추천 기능 구현
	- 사용자 조회 이력 기반의 추천 다양성 확보 알고리즘 구현 및 적용

<br>

## 업데이트 이력
- [2024-07-23 나현진] 유저 CRUD & 로그인, 명언 CRUD, postgreSQL 연결 및 초기화
- [2024-07-28 정혜나] Quote CRUD, 좋아요, 댓글 기능 구현, account ProfileView 추가
- [2024-07-29 남기동] account 필드 제거, superuser 수정, Quote output field 조정
- [2024-07-29 정혜나] 사용자가 명언 Post 기능 구현, ProfileView 수정
- [2024-07-30 남기동] Chroma 연결, Quote CRUD와 연동, CommentAdminView 생성, 명언 추천 기능 구현, 명언 좋아요 내림차순 조회 구현
- [2024-07-31 남기동] 서버 설정 관련 명령어(server.md) 업로드, settings.py의 ALLOW_HOST=['*']로 변경(외부 접속 허용을 위해)
- [2024-07-31 정혜나] 팔로잉 기능 구현
- [2024-08-01 남기동] 유저 명언 조회, 조회 기록 삭제, 프로필 수정/삭제
- [2024-08-07 남기동] 서버 파일들로 최종 업데이트

<br>

## 설치방법

```bash
$ git clone https://github.com/mukzzanglion-team2/new_backend.git
$ cd new_backend
$ python -m venv venv
$ source ./venv/Scripts/activate
$ pip install -r requirements.txt

# 필요에 따라 PostgreSQL Docker Container 생성 및 실행
$ docker run -p 5432:5432 --name test-postgres -e POSTGRES_PASSWORD=1234 -e TZ=Asia/Seoul -d postgres:latest
# docker exec -it {container_id} bash --> psql -U postgres --> create database quote_db; --> exit --> exit

# CircularDependency 에러 처리를 위해
# accounts, quote의 models.py에 ForeignKey, ManyToManyField 주석처리하고
$ python manage.py makemigrations account
$ python manage.py makemigrations quote
$ python manage.py migrate

# accoutns, quote의 models.py에 주석처리한 부분 해제하고
$ python manage.py makemigrations account
$ python manage.py makemigrations quote
$ python manage.py migrate

$ python manage.py createsuperuser
# email, nickname, password 입력하면 유저 생성

$ python manage.py runserver
```


## .env 파일
```
# Public이므로 KEY 관련 값들은 삭제하였습니다
SECRET_KEY = ''
KAKAO_REST_API_KEY=''
DB_NAME= 'quote_db'
DB_USER='postgres'
DB_PASSWORD='1234'
DB_HOST='localhost'
DB_PORT='5432'
UPSTAGE_API_KEY = ""
OPENAI_API_KEY = ""
CHROMA_HOST = "127.0.0.1"
CHROMA_PORT = "8001"
ALGORITHM='HS256'
```


## Directory Tree
```
project/
├── config/
│   ├── apps.py         	# App 초기화 설정
│   ├── settings.py		
│   ├── ...
│   └── urls.py         
├── account/            	# User, Login 관련
│   ├── models.py       	
│   ├── serializers.py
│   ├── urls.py         	# URL Mapping
│   ├── ...
│   └── views.py        	# 웹 요청 처리
├── quote/              	# 명언 관련
│   ├── models.py     
│   ├── serializers.py
│   ├── urls.py         	# URL Mapping
│   ├── ...
│   └── views.py        	# 웹 요청 처리
├── database/           	# Chroma, DB 세팅 관련
│   ├── chroma_manager.py	# Chroma 관련 함수 정의
│   ├── database.py		# Chroma 연결 
│   ├── DB_setting.ipynb   	# DB 초기 세팅을 위한 함수
│   ├── ...
│   └── quote_example.json    	# 명언 100개 데이터
├── manage.py          
├── requirements.txt    	# 의존성
├── server.md           	# 서버 설정 관련 가이드라인
├── .env                	# 환경 변수 파일
├── .gitignore
├── media/profile_images 	# MEDIA 경로        
└── venv/               	# 가상 환경
```


## Model Schema
```javascript
User {
	id : PK(auto_increment)
	
	# Not NULL
	email : email
	password : str(~30)
	nickname : str(~50)
	profile_image : ImageField(null=True)
	
	# NULL
	liked_quotes : List[quote_id] = []
	followings : List[user_id] = []
	follower_count : PositiveInteger = 0
	follwing_count : PositiveInteger = 0
	is_active : True
	is_staff : False(superuser만 True)
}

Quote {
	id : PK(auto_increment)
	
	# Not NULL
	content: str(~100)
	description : str(~800)   
	author : str(~100)        # 해당 명언의 발화자(원저작자)
	
	# NULL
	image : ImageField
	created_at : Datetime
	like_count: PositiveInteger
	quote_viewers : List[User] = []	 # 해당 명언 조회 유저, 매일 오전 6시마다 초기화
}

Comment {
	id : PK(auto_increment)

	# Not NULL
	content : TextField
	quote : Quote.id
	user : User.nickname

	# NULL
	created_at : Datetime
}
```


## 참고할 노션 페이지
<https://www.notion.so/rmdnps10/Back-End-60d517d1690b44bc9d4c0ded0b839ec9>
