# Packet_Gen

패킷 가상 데이터 셋을 만들어 내기 위한 프로그램.
- Config 폴더 내 [Device / User / Home]Config.json을 수정하고 실행
- Output : csv ( columns = Time / srcIP / srcPort / dstIP / dstPort / Packetsize / SessionID / vendor ) 

### 데이터 생성 규칙
- 각 기능이 실행 되는 시간은 (실행 시간 + 데이터 이동 시간)으로 규정된다.
- 실행 시간의 경우 사용자가 입력하는 시간 값을 가지고 bias를 더해서 생성하고 데이터 이동시간의 경우 해당 작업으로 만들어진 데이터가 주어진 네트워크 속도에 대해 얼마만큼의 시간이 소요되는지 계산하고 이를 더한다.
- 펌웨어 업데이트의 경우 랜덤하게 펌웨어 다운로드 여부를 확인하고 업데이트가 있다면 즉시 펌웨어 다운로드 패킷을 생성
- 세션 넘버는 65000번까지 랜덤 추출
- 사용자의 기기 사용을 구분하기 위해 각 기기내 기능 명앞에 해당 장비 이름 삽입해 네이밍 한다.
- 중복작업을 처리하기 위해서 Taskname_#와 같은 표기를 한다.

### Configuration 설명
1. HomeConfig.json Setting
  - IP : 개별 기기에 할당할 아이피의 Base IP(서브넷일 경우 개별 기기에 서브넷에 해당하는 ip로 할당)
  - from_date : 패킷 생성의 시작 시간 
  - to_date : 패킷 생성의 종료 시간
  - Devices :  해당 패킷 생성 환경에 두게 될 Devices name / 각각의 Device들은 DeviceConfig.json에 정의 되어야함
  - User_setting : 해당 패킷 생성 환경에 두게 될 User type / 각각의 User type은 UserConfig.json에 정의 되어야함
  - Network_speed_per_sec : 패킷 생성 환경의 초당 바이트 다운로드 속도(업로드 속도 = 다운로드 속도)

2. DeviceConfig.json Setting
  - Device는 개별 기능들의 묶음으로 하나의 기기가 정의됨
  - 따라서 개별 기능들을 정의하는 것이 한개의 Device를 만들어 내는 것임.
  - Json의 구조는 "Device name : { Function_name : { Task : [Common / Streaming / Repeatedly], Session : [Connection_# / Streaming / stage]의 형태를 가지고 있음
    - Task 구분
      - Common의 경우 특정한 시간대에 일어나는 이벤트성 패킷을 정의할 때 사용
      - Streaming의 경우 Common의 특수한 케이스로 특정시간대에 일어나지만 지속적인 패킷 다운로드가 있는 경우 사용
      - Repeatedly 경우 일정한 간격으로 발생되는 패킷이 있는 경우 사용
    - Session 구분
      - Connection_#는 일반적인 UP/DN으로 이루어진 커넥션
        - Client_specific_port의 경우 특정 Connection안에 존재하는데 이는 클라이언트가 특정 포트를 통해서 통신을 해야만 할때 사용함
        - Common Task일 경우의 Connection의 일반적인 구성
          - Server / Server_PortRange / UPDN / working_time / packet
        - Repeatedly Task일 경우의 Connection의 일반적인 구성
          - Server / Server_PortRange / UPDN / working_time / packet / interval1 / interval2
          - interval1은 아라비아 숫자 / interval2는 시간단위
      - Streaming의 경우 Task가 Connection의 일반적인 구성
        - Server / Server_PortRange / UPDN / working_time / packet / standard_trial_time_min
        - time의 내 마지막 정의 되는 소요시간이 패킷의 다운로드 시간으로 규정됨
        - standard_trial_time_min 재생 곡들의 평균적인 소요 시간 (분)
        - streaming을 사용하는 Useraction이 있는 경우 UserConfig내에 max_stream_time을 규정지어야함
        - 스트리밍 기능을 구현하고 싶은 경우 Connection_#과 streaming을 순차적으로 사용하면 가능
        - streaming으로 구현되어 있는 커넥션의 마지막 다운로드 패킷을 주어진 시간에 대해 다운로드 받게됨.
      - stage는 해당 기능이 순차적으로 어떤 커넥션을 가지는 지 규정.
        - 실제 패킷 생성시에는 stage를 읽은 후에 하위 커넥션들을 찾고 이를 단위 패킷으로 구성해 나감.

3. UserConfig.json Setting
  - User의 경우 특정기기에 대한 명령이 User type을 정의함
  - Json의 구조는 "User_type : { weekday / weekend : { Task_name : { start_time, finish_time, max_trial ,(max_stream_time)
  - 개별 Task(Task_name) 를 주어진 시작시간(start_time)과 종료시간(finish_time)내 최대 몇번(max_trial)을 실행한다 라는 구조임.
  - Task가 streaming 일 경우 최대 스트리밍 시간(max_stream_time)을 지정해 주어야함.
  - Streming의 경우 최대 스트리밍 시간 만큼 작업이 지속될 수 있음.
 
 4. Anomaly Configuartion
  - DDOS / Port_scan 두가지 구현
  - DDOS의 경우 특정 기기가 감염되어 외부로 커넥션을 맺는 패킷을 다량 생성하는 시나리오 적용
  - 감염된 기기에서만 나타나기 때문에 개별 기기 config세팅시 botnet으로 구현
  - botnet의 경우 기존 기능과 동일하게 userconfig에서 시작시간 / 종료 시간 / 최대 횟수를 정해주어야 함.
  - Port_scan의 경우 AP에 대해 외부에서 무작위로 포트를 확인하는 방식으로 시나리오 적용
  - port_scan의 경우 AP장비를 구현하고 해당 장비에 port_scan이라는 기능명으로 구현

 ### Excecution
 0. Set Configurations
 1. python data_gen_v2.py
 2. After Executing it, output files are in ./PacketGen/Home(1,2,3..).log
 3. (optional plotting function) python Plotting.py {logfile} {outname} {resample_seconds}
