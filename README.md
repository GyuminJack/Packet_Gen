# Packet_Gen

세션별 가상 패킷을 만들어 내기 위한 코드.

전체적인 구성은 다음과 같다.

Configuration 
1. Device setting
  - 기기는 기능의 합으로 규정된다.
  - 각각의 기능을 정의한다.
  - "traffic_check" : {
            "Server" : "123.234.23.",
            "PortRange" : [300,301],
            "UPDN" : ["UP","DN","UP","DN"],
            "time" : [1,2,3,4],
            "packet" : [1,1,2,3]
            
2. User Setting
  - 각 유저는 행동 패턴의 합으로 규정된다.
  - 행동패턴은 주중과 주말로 나누어 구성한다.
  -  "USER1" : { 
        "weekday" : {
            "traffic_check" : {"Hour":7, "Min":59},
            "find_info" : {"Hour":10, "Min":0}
        },
        "weekend" : {
            "traffic_check" : {"Hour":1, "Min":10},
            "find_info" : {"Hour":2, "Min":0}
        }

3. Home Setting
  - 각 Home은 고유 IP와 PORT를 가진다.
  
