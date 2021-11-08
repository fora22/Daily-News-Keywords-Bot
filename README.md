# Daily News Keywords Bot

# 프로젝트 소개
### 뉴스 데이터를 집계해서 트렌드를 파악하는 서비스

매일 뉴스 데이터를 수집하고 가공한 뒤 세부 섹션 별로 자주 등장했던 키워드를 시각화하고 메시지로 전송합니다.

실시간 검색어 서비스가 종료된 이후 하루의 중요 키워드가 무엇인지 한 눈에 파악하기가 어려워졌습니다. 따라서 뉴스 제목 데이터를 수집해서 자주 등장하는 키워드를 기반으로 이슈와 트렌드를 파악하는 데에 활용해보고자 했습니다.


---

# 데이터 파이프라인
![Daily-Keywords-Bot](https://user-images.githubusercontent.com/54028026/135100050-1a99aae9-1199-4c5f-8747-0822ce464cb9.png)

---

### (1) ETL
네이버, 다음 뉴스를 수집합니다. 프로듀서는 로우 데이터를 bson 형태로 가공한 뒤 DW(Data Warehouse)에 적재합니다.

### (2) Processing
명사 추출기는 DW에 적재한 로우 데이터에서 뉴스 제목 데이터의 명사를 추출 하고 변환한 뒤 Data Mart  ES(ElasticSearch)에 적재합니다.

### (3) Service
가공한 데이터로 대시보드를 생성합니다. 또한 집계 작업을 거친 뒤 슬랙 채널에 알림 메시지를 전송합니다.


# 1. ETL
## Extract & Transform
네이버와 다음 뉴스 서비스에서 오늘 날짜에 해당하는 기사 제목과 URL을 수집해서
‘portal’ + ‘date’ + ‘.txt’ 파일 형태로 로우 데이터를 저장합니다. ex) NAVER20211031.txt 

프로듀서는 로우 데이터를 미리 정의해둔 bson 스키마 형태로 변환합니다. 만약 변환 과정에서 문제가 생기는 경우 fail 항목에 추가하여 후처리가 가능하도록 예외처리 합니다.


## Load
도큐먼트 기반의 NoSQL 데이터베이스인 Mongo DB를 데이터 웨어하우스로 사용합니다. 프로젝트 초반에는 초반에는 하둡을 사용하기 위해 Hbase를 고려했으나 일일 수집 데이터 사이즈가 10MB가 채 되지 않기 때문에 오버 엔지니어링이라고 판단했습니다. 또한 와이드 컬럼 기반의 NoSQL 데이터베이스의 경우 빈번한 집계 및 통계 작업에서의 이점이 존재하지만 본 프로젝트의 데이터 웨어하우스는 일일 한 번씩 데이터를 요청하는 용도이므로 별도의 이점이 없기도 했습니다. 뉴스 데이터의 특징은 날짜가 존재하고 기사(데이터) 한 건이 문서로 표현될 수 있으므로 도큐먼트 기반의 NoSQL을 선택했습니다.

news 라는 네임으로 DB를 생성하고 날짜를 컬렉션 네임으로 설정하여 데이터 검색과 관리 측면에서의 편의를 지향하고 있습니다. 

데이터 레이크가 아닌 웨어하우스이므로 규격화된 스키마를 가지고 있습니다. 만약 수집한 데이터가 미리 지정한 bson 스키마에 부합하지 않는 경우 fail 리스트에 추가하여 후처리를 진행할 수 있는 예외처리 로직이 존재합니다.




## 몽고디비 컬렉션
<img width="750" alt="DW_컬렉션" src="https://user-images.githubusercontent.com/54028026/140729484-a02e5349-eb9a-46a3-8547-94fbea8ac8c4.png">


평일 약 4.5만건, 주말 약 2.2만 건 정도를 수집하고 있습니다. 

프로젝트 초반에는 url을 유니크 인덱스로 활용하여 수집 단계에서 중복 제거를 시도했습니다. 그러나 유니크 인덱스의 경우 직관적으로 데이터 한 건을 대표할 수 있어야하므로 사용하지 않기로 결정했습니다.



## 로우 데이터 예시
<img width="750" alt="DW_데이터적재" src="https://user-images.githubusercontent.com/54028026/140729485-2dd96380-b0f1-4052-8bd5-075ba9c4cd4f.png">

다음뉴스의 자동생성 기사, 보도 자료와 같이 세부 섹션이 없는 경우는 null로 처리합니다.

---

# 2. Processing

Konlpy에서 제공하는 Okt 모듈을 사용해서 뉴스 제목 데이터에서 명사를 추출하고 가공한 데이터를 ES에 적재합니다. 
(뉴스 제목에서 명사만 추출한 뒤 배열 형태로 변환합니다.)

ES 및 Kibana는 ELK 스택 학습 목적으로 본 프로젝트에 활용하고자 했습니다. 적재한 데이터를 Kibana를 통해 간편하게 시각화 할 수 있는 점이 매력적입니다. ES의 경우 인덱스 기반의 NoSQL이며 검색에 이점이 있는 것은 알고있지만 아직 얕은 이해도에 머물러있기 때문에 추가적으로 학습하고 정리할 예정입니다.

## Raw data Processing
![raw_data_processing](https://user-images.githubusercontent.com/54028026/140731423-5b6b9f44-4493-4a4a-814f-863fe7248584.png)

명사 추출기는 다양하게 테스트 하면서 Okt 모듈이 목적에 맞는 결과를 보여주어 선택하게 되었습니다.

## Data Mart
<img width="1432" alt="Service_Kibana_Discover" src="https://user-images.githubusercontent.com/54028026/140731500-3984af5e-5139-4e74-847b-33a5088c6820.png">

키바나에서 엘라스틱 서치에 적재한 데이터를 확인할 수 있습니다. 
리얼 타임 서비스가 아니므로 날짜 데이터는 시간 값을 지정하지 않았습니다. 따라서 09시로 시간값이 고정됩니다.

---

# 3. Service
## Keywords Dashboard

엘라스틱 서치에 적재한 데이터를 키바나를 활용하여 시각화합니다. 자체적으로 타임스탬프 필터링 기능을 가지고 있으므로 추가 작업 없이 업데이트됩니다. 
(Kibana 외에도 ES를 지원하는 시각화 솔루션이라면 자유롭게 활용할 수 있습니다. ex) Tableau )

<img width="1400" alt="Service_Kibana_Visualization" src="https://user-images.githubusercontent.com/54028026/140729475-6b04bc05-2457-46c0-a4f6-82d8232021dd.png">

---

## Notification Bot

엘라스틱 서치에 오늘 날짜에 해당하는 데이터를 요청하고 집계 작업을 실시합니다. 집계 결과를 포털, 세부 섹션 별로 구분하여 빈출 상위 3개 키워드를 슬랙 채널에 전송합니다. 만약 카운팅이 동률인 경우 모두 포함하여 전송합니다.

<img width="1400" alt="슬랙봇" src="https://user-images.githubusercontent.com/54028026/140484490-ea5d3aeb-c9de-4271-8498-18d6075ae08e.png">



---

# Scheduling
배치 스케줄링 툴로 Airflow를 활용했습니다. 각각의 작업은 크론을 활용할 수 있으므로 초기에는 도입 여부에 관해 고민했습니다만 최근 Airflow에 대한 관심을 가지게 되어서 학습 목적으로 활용하게 되었습니다. Airflow를 활용하면 각 컴포넌트의 의존관계를 설정할 수 있으며 진행 상황을 시각 이미지로 한 눈에 파악할 수 있다는 점이 편리합니다. (사용한 2.14버전의 경우 디폴트 타임존 옵션이 제공되나 KST로 설정해도 UTC 기반으로 작동하는 문제가 있습니다.)


## DAG Graph
<img width="1400" alt="Scheduling_Airflow1" src="https://user-images.githubusercontent.com/54028026/140731632-cda9820f-acdb-4bae-844b-f6286a6ed185.png">


## Tree View 
<img width="1400" alt="Scheduling_Airflow2" src="https://user-images.githubusercontent.com/54028026/140731637-1d7ab1be-04c8-429e-b214-f79242ef1a25.png">
---

