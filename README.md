# Daily News Keywords Bot

# 프로젝트 소개
뉴스 데이터를 집계하고 알림을 보내주는 서비스입니다. 매일 뉴스 데이터를 수집해서 자주 등장하는 키워드를 기반으로 대시보드 업데이트 및 알림 메시지를 전송합니다.

실시간 검색어 서비스가 종료된 이후 하루의 중요 키워드가 무엇인지 한 눈에 파악하기가 어려워졌습니다. 따라서 뉴스 제목 데이터를 수집해서 자주 등장하는 키워드를 기반으로 오늘의 이슈와 트렌드를 파악하는 데에 활용해보고자 했습니다.



---

# 데이터 파이프라인
![Daily-Keywords-Bot](https://user-images.githubusercontent.com/54028026/135100050-1a99aae9-1199-4c5f-8747-0822ce464cb9.png)

데이터 파이프라인은 크게 3단계로 구성되어 있습니다.


### 1. ETL
크롤러는 각각 네이버, 다음 뉴스를 수집하여 저장합니다. 프로듀서는 로우 데이터를 bson 형태로 가공한 뒤 데이터 웨어하우스에 적재합니다.

### 2. 데이터 가공
명사 추출기는 DW에 데이터를 요청한 뒤 뉴스 제목 데이터의 명사를 추출 하고 변환한 뒤 데이터 마트에 적재합니다.

### 3. 서비스
가공한 데이터로 워드 클라우드 대시보드를 생성합니다. 또한 집계 작업을 거친 뒤 슬랙 채널에 알림 메시지를 전송합니다.


---

# 1. ETL
## (1) 데이터 수집
크롤러는 각각 네이버와 다음 뉴스 서비스에서 오늘 날짜에 해당하는 기사 제목과 URL을 모두 수집한 뒤 ‘portal’ + ‘date’ + ‘.txt’ 파일 형태로 로우 데이터를 저장합니다. ex) NAVER20211031.txt 

[이미지]

## (2) 데이터 변환
프로듀서는 로우 데이터를 미리 정의해둔 bson 스키마 형태로 변환합니다. 만약 스키마에 적합한 형태로 변환하는 과정에서 문제가 생기는 경우 fail 항목에 추가하여 후처리가 가능합니다. 

[이미지]


## (3) 데이터 적재
도큐먼트 기반의 NoSQL 데이터베이스인 Mongo DB를 데이터 웨어하우스로 사용합니다. 뉴스 데이터의 특징은 날짜가 존재하고 기사(데이터) 한 건이 문서로 표현될 수 있기 때문입니다. 

news 라는 네임으로 DB를 생성하고 날짜를 컬렉션 네임으로 설정하여 데이터 검색과 관리 측면에서의 편의성을 지향합니다.

프로젝트 초반에는 초반에는 하둡을 사용하기 위해 Hbase를 고려했으나 일일 수집 데이터 사이즈가 10MB가 채 되지 않기 때문에 오버 엔지니어링이라고 판단했습니다. 또한 와이드 컬럼 기반의 NoSQL 데이터베이스의 경우 빈번한 집계 및 통계 작업에서의 이점이 존재하지만 본 프로젝트의 데이터 웨어하우스는 일일 한 번씩 데이터를 요청하는 용도이므로 별도의 이점이 없다고 판단했습니다.



### 데이터 웨어하우스 관리 예시
<img width="1200" alt="몽고디비_데이터웨어하우스" src="https://user-images.githubusercontent.com/54028026/140483802-9574571c-0c97-46b2-bf00-f9b069a08d62.png">

수집하는 데이터를 구분하는 가장 첫 번째 기준은 시간이라고 할 수 있습니다. 따라서 컬렉션 네임을 날짜로 설정하여 데이터 관리 측면에서의 편의성을 지향했습니다. 

### 수집 데이터 예시
<img width="1200" alt="몽고디비_컬렉션" src="https://user-images.githubusercontent.com/54028026/140483822-c1639c10-f188-4f62-a547-98a5ff9a82b1.png">

데이터 레이크가 아닌 웨어하우스이므로 규격화된 스키마를 가지고 있습니다. 만약 수집한 데이터가 미리 지정한 bson 스키마에 부합하지 않는 경우 fail 리스트에 추가하여 후처리를 진행할 수 있도록 예외처리를 했습니다.

---

# 2. Processing

ElasticSearch에 적재한 데이터는 Kibana를 활용하여 간편하게 시각화를 할 수 있으며 별도의 추가 작업없이 대시보드를 업데이트를 할 수 있으므로 데이터 마트로 채택했습니다.

명사 추출기는 오늘 날짜에 해당하는 데이터를 데이터 웨어하우스에 요청하고, 레코드의 뉴스 제목에서 명사만 추출하여 배열로 변환하고 엘라스틱 서치에 적재합니다. (명사 추출기는 konlpy의 okt를 활용했습니다.)


### 데이터 마트에 적재한 데이터 예시
<img width="1427" alt="엘라스틱서치_데이터마트" src="https://user-images.githubusercontent.com/54028026/140483831-85de6cd5-3e07-4461-82cd-489b19a94211.png">


---

# 3. Service
## (1) 시각화 대시보드

엘라스틱 서치에 적재한 데이터를 키바나를 활용하여 시각화합니다. 자체적으로 타임스탬프 필터링 기능을 가지고 있으므로 추가적인 대시보드 작성없이 업데이트됩니다.

### 대시보드 예시
<img width="1440" alt="키바나_대시보드" src="https://user-images.githubusercontent.com/54028026/140483828-86e652f1-fa26-4968-8e64-f2a180356c5c.png">


[워드 클라우드 이미지]

---

## (2) 키워드 알림 봇

엘라스틱 서치에 오늘 날짜에 해당하는 데이터를 요청하고 집계 작업을 실시합니다. 포털, 세부 섹션 별로 자주 등한 상위 3개 키워드를 집계한 뒤 슬랙으로 메시지를 전송합니다. 만약 카운팅이 동률인 경우 모두 포함하여 전송합니다. 

### 알림 봇 메시지
<img width="1431" alt="슬랙봇" src="https://user-images.githubusercontent.com/54028026/140484490-ea5d3aeb-c9de-4271-8498-18d6075ae08e.png">



---

## 4. 스케줄링
배치 스케줄링 툴로 Airflow를 활용했습니다. 각각의 작업은 크론을 활용할 수 있으므로 초기에는 도입 여부에 관해 고민했습니다. 그런데 최근 Airflow에 대한 관심을 가지게 되어서 학습 목적으로 활용하게 되었습니다.

Airflow를 활용하면 각 컴포넌트를 한 번에 관리할 수 있으며 각 과정의 진행 상황을 시각 이미지로 한 눈에 파악할 수 있다는 점이 매력적입니다.


<img width="1419" alt="에어플로우_스케줄링" src="https://user-images.githubusercontent.com/54028026/140483817-e8d45818-3b6e-4d40-8366-8b1521ae6d74.png">

---





기술 스택을 활용하는 이유에 관해
- 몽고디비: 가장 익숙한 오픈 소스 NoSQL 디비이면서 사용하기 쉽다. 몽고 익스프레스를 활용하며 웹 기반으로 관리가 가능한 것도 장점이다. 도큐먼트를 대표하는 키를 인덱스를 생성할 경우 쿼리로 탐색도 빠른편이다. 유니크 인덱스의 경우 O(logN) 정도의 시간복잡도라고 한다.
- 엘라스틱 서치: 도큐먼트 하나에 명사들을 배열로 저장했을 때 키바나로 시각화하기 쉽다. 다중 필드 조건으로 쿼리를 날려서 가공한 데이터를 처리하기에도 좋다.
- 에어플로우: 메인 랭귀지가 파이썬이며 해당 프로젝트는 배치 처리이며 각각의 컴포넌트들이 의존성을 가지므로 에어플로우가 스케줄링 툴로 적합하다.



