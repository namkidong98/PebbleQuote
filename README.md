# new_backend



## 업데이트 이력
- [2024-07-23 나현진] 유저 CRUD & 로그인, 명언 CRUD, postgreSQL 연결 및 초기화

<br>

## 설치방법

```
git clone https://github.com/mukzzanglion-team2/new_backend.git
cd new_backend
python -m venv venv
source ./venv/Scripts/activate
pip install -r requirements.tx
```




## .env 파일
```
SECRET_KEY = 'django-insecure-p8+g6!$v=)5e3_bfwn&la9f8y95ccx=awv&3$-t1oe(nkgcbsf'
KAKAO_REST_API_KEY='217fcb126e662a8cbaa60bff80aa32df'
DB_NAME= 'quote_db'
DB_USER='root'
DB_PASSWORD='likelion12th_quote'
DB_HOST='localhost'
DB_PORT='5432'
```





## Directory Tree
```
project/
├── config/
│   ├── apps.py         
│   ├── settings.py
│   ├── ...
│   └── urls.py         
├── account/            # User, Login 관련
│   ├── crud.py         
│   ├── serializers.py
│   ├── urls.py         # URL Mapping
│   ├── ...
│   └── views.py        # 웹 요청 처리
├── quote/              # 명언 관련
│   ├── crud.py         
│   ├── serializers.py
│   ├── urls.py         # URL Mapping
│   ├── ...
│   └── views.py        # 웹 요청 처리
├── manage.py          
├── requirements.txt    
├── .env                # 환경 변수 파일
├── .gitignore        
└── venv/               # 가상 환경
```






## Model Schema
```
User {
	_id : ObjectID(자동 생성, PK)
	
	# Not NULL
	email : email
	password : str(~30)
	nickname : str(1~20)
	name : str(~50)
	age : int(1~100)
	sex : Literal['male', 'female']
	birth : str(format:2000-01-01)
	phone : str(format:010-0000-1111)
	
	# NULL --> []로 초기화
	followers : List[user_id] = []
	following : List[user_id] = []
	regiestered_quotes : List[quote_id] = []
	liked_quotes : List[quote_id] = []
}

Quote {
	_id : ObjectID(자동 생성, PK)
	
	# Not NULL
	content: str(~100)
	description : str(~500)   
	author : str              # 해당 명언의 발화자(원저작자)
	registrant : str(user_id) # 등록한 사람(User)
	tag : List[str]
	
	# NULL --> []이나 NULL, 0으로 초기화
	image : ImageField
	likes: int
	comments : List[str] = []
	created_at : datetime
}
```





## 참고할 노션 페이지
<https://www.notion.so/rmdnps10/Back-End-60d517d1690b44bc9d4c0ded0b839ec9>






