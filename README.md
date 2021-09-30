# Daily News Keywords Bot
## 프로젝트 동기
실시간 검색어가 사라진 후로 그날그날 중요 키워드를 확인하기가 어렵다.
최근에는 시간상 뉴스를 매일 챙겨보는 것도 어려워졌다. 
그렇다면 뉴스에 자주 등장하는 키워드들을 추출해서 메신저로 알림을 보내주는 서비스를 개발 어떨까? (주식 투자에도 도움이 될 것 같다.)

---

## 아키텍처
![Daily-Keywords-Bot](https://user-images.githubusercontent.com/54028026/135100050-1a99aae9-1199-4c5f-8747-0822ce464cb9.png)

---

## 청사진
1. 데이터 수집 ✓
2. 데이터 레이크 - MongoDB ✓
3. 전처리 크론탭 ✓
4. 데이터 마트 - Elastic Search ✓
5. 시각화 - Kibana ✓
6. 알림 봇 - Slack ✓ 
7. 스케쥴링 - Airflow

* 가능한 각 컴포넌트들을 분리해서 유지보수가 쉽게 개발하는 것을 목표로하기
* 만약 적재 데이터 사이즈가 많이 커졌고, 스파크를 활용해서 데이터를 처리하고 싶다면 HDFS를 추가로 붙이는 것도 방법

---

잘못들은 습관?
프로젝트에서 사용하는 데이터 사이즈를 고려하지 않고 하둡을 사용하려하는 점
데이터 파이프라인의 레이어가 간결할 수록 유지보수는 쉽다. 
간결한 레이어에서 데이터 사이즈가 커져서 감당할 수 없다면 추가적인 컴포넌트를 고려한다.
