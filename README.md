# Daily News Keywords Bot
## 프로젝트 동기
실시간 검색어가 사라진 후로 그날그날 중요 키워드를 확인하기가 어렵다.
최근에는 시간상 뉴스를 매일 챙겨보는 것도 어려워졌다. 
그렇다면 뉴스에 자주 등장하는 키워드들을 추출해서 메신저로 알림을 보내주는 서비스를 개발 어떨까? (주식 투자에도 도움이 될 것 같다.)

---

## 데이터 파이프라인
![Daily-Keywords-Bot](https://user-images.githubusercontent.com/54028026/135100050-1a99aae9-1199-4c5f-8747-0822ce464cb9.png)

---

## To Do
1. 데이터 수집 ✓
2. 데이터 레이크 - MongoDB ✓
3. 전처리 크론탭 ✓
4. 데이터 마트 - Elastic Search ✓
5. 시각화 - Kibana ✓
6. 알림 봇 - Slack ✓ 
7. 스케쥴링 - Airflow ✓ (No Super User)
8. 다음 뉴스 크롤러 개발 ✓
9. *문서화 - 프로젝트 정리 및 새롭게 배운 내용들(ES 쿼리 및 에어플로우) -> 미진행.. 10월 마지막주에 정리
10. 워드 클라우드 시각화가 더 직관적이지 않을까란 피드백을 받았는데, 굉장히 좋은 아이디어 같다. -> 키바나 워드클라우드 지원하는 것으로 확인 ✓
11. 에어플로우 로컬 서버 타임으로 작동하는지 확인 하기 -> 서버타임으로 시작하지 않는 문제


* 가능한 각 컴포넌트들을 분리해서 유지보수가 쉽게 개발하는 것을 목표로하기
* 만약 적재 데이터 사이즈가 많이 커졌고, 스파크를 활용해서 데이터를 처리하고 싶다면 HDFS를 추가로 붙이는 것도 방법
---

- 잘못들은 습관?
프로젝트에서 사용하는 데이터 사이즈를 고려하지 않고 하둡을 사용하려하는 점
데이터 파이프라인의 레이어가 간결할 수록 유지보수는 쉽다. 
간결한 레이어에서 데이터 사이즈가 커져서 감당할 수 없다면 추가적인 컴포넌트를 고려한다.

---
기술 스택을 활용하는 이유에 관해
- 몽고디비: 가장 익숙한 오픈 소스 NoSQL 디비이면서 사용하기 쉽다. 몽고 익스프레스를 활용하며 웹 기반으로 관리가 가능한 것도 장점이다. 도큐먼트를 대표하는 키를 인덱스를 생성할 경우 쿼리로 탐색도 빠른편이다. 유니크 인덱스의 경우 O(logN) 정도의 시간복잡도라고 한다.
- 엘라스틱 서치: 도큐먼트 하나에 명사들을 배열로 저장했을 때 키바나로 시각화하기 쉽다. 다중 필드 조건으로 쿼리를 날려서 가공한 데이터를 처리하기에도 좋다.
- 에어플로우: 메인 랭귀지가 파이썬이며 해당 프로젝트는 배치 처리이며 각각의 컴포넌트들이 의존성을 가지므로 에어플로우가 스케줄링 툴로 적합하다.

---
### 컴포넌트 역할 요약
1. 크롤러 - 뉴스 데이터 수집 및 저장
2. 프로듀서 - 수집한 뉴스 데이터를 데이터 웨어하우스에 저장
3. 데이터 웨어하우스 - 몽고디비의 컬렉션을 날짜로 생성하여 뉴스 데이터를 저장
4. 컨슈머(명사 추출) - 데이터 웨어하우스에 저장한 뉴스 데이터의 명사를 추출하여 엘라스틱 서치에 저장
5. 데이터 마트 - 가공한 날짜, 포털, 카테고리, 세부 카테고리, 명사 리스트 데이터를 저장
6. 시각화 - 키바나를 활용하여 엘라스틱 서치의 인덱스를 시각화
7. 슬랙 봇 - 엘라스틱 서치에 오늘 날짜를 기준으로 쿼리를 날려서 포털 및 세부 뉴스 별로 명사 카운팅 후 메세지 발송
