# working-title


## 프로젝트 동기
실시간 검색어가 사라진 후로 그날그날 중요 키워드를 확인하기가 어렵다
뉴스를 매일 챙겨보는 것도 어려워
그래서 화제인 키워드들을 매일 저녁 그리고 아침마다 받아볼 수 있는 솔루션을 개발해서 사용해보면 어떨까?

## 청사진
1. 데이터 수집
2. 데이터 레이크(kafka)
3. 장기 데이터 적재 (하둡에 에이브로)
4. noSQL을 활용한 버퍼 스토리지 적용
5. 배치 타임으로 nosql에 저장한 데이터를 전처리하고 전송하는 
6. 배치 처리로 Elastic search에 적재 후 시각화
7. 정해진 시간마다 쿼리날리고 메신저로 알림 (신청한 사용자의 옵션에 따라서 이건 가볍게 레디스를 사용해도 )
