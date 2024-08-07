# new_backend


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

## 서버 이용 방법
- pem키 사용 없이 ID, Password로 접속 가능하게 변경해두었습니다
- Putty에서 Host Name에 15.164.27.255, Port 22로 설정하고 Open
- ID : ec2-user
- PASSWORD : shinsudong
- (확인용) 'http://15.164.27.255/quote/', 'http://15.164.27.255/accounts/register/' 로 체크 가능
- (Admin 'http://15.164.27.255/admin/' ) Email : admin@google.com, Password : admin 


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
