# Packet_Gen

세션별로 묶인 가상 데이터 셋을 만들어 내기 위한 프로그램.
- Config 폴더 내 [Device / User / Home] json을 수정하고 실행
- Output : csv ( columns = Time / srcIP / srcPort / dstIP / dstPort / Packetsize / SessionID / vendor ) 

### 데이터 생성 규칙
- 각 기능이 실행되는 시간을 중심으로 정규분포를 만들고 랜덤추출을 통해 실행 시간 설정
- 펌웨어 업데이트의 경우 랜덤하게 펌웨어 다운로드 여부를 확인하고 펌웨어 다운로드 패킷을 생성
- 연속되어 실행되는 기능의 경우 직전 작업이 끝나자 마자 동일한 방식으로 실행
- 기본 패킷의 추출 단위는 1초단위로 설정
- 세션 넘버는 65000번까지 랜덤 추출
- 1초 이상 소요되는 작업의 경우 총 다운로드 패킷에 대해 1초단위로 나누어 전송
- 사용자의 기기 사용을 구분하기 위해 각 기기내 기능 명앞에 해당 장비 이름 삽입
- 기기에서 발생하는 serverIP의 경우 c 클래스로 적용하지만 펌웨어의 경우 특정 IP로 구성
- 각 세션에서 발생되는 포트는 해당 기기의 포트 범위에서 난수 생성 하지만 포트 범위가 1 차이가 날 경우 앞 숫자의 포트로 고정
- 중복작업을 처리하기 위해서 Taskname_#와 같은 표기를 한다.

### Configuration 
1. HomeConfig.json Setting
  - IP : 개별 기기에 할당할 아이피의 Base IP (c class)
  - from_date : 패킷 생성의 시작 시간 
  - to_date : 패킷 생성의 종료 시간
  - Devices :  해당 패킷 생성 환경에 두게 될 Devices name / 각각의 Device들은 DeviceConfig.json에 정의 되어야함
  - User_setting : 해당 패킷 생성 환경에 두게 될 User type / 각각의 User type은 UserConfig.json에 정의 되어야함
  
2. DeviceConfig.json Setting
  - Device는 개별 기능들의 묶음으로 하나의 기기가 정의됨
  - 따라서 개별 기능들을 정의하는 것이 한개의 Device를 만들어 내는 것임.
  - Json의 구조는 "Device name : { Function_name : { Task : [Common / Streaming / Repeatedly], Sessions : [Session_# / Streaming / Routine]의 형태를 가지고 있음
    - Task 구분
      - Common의 경우 특정한 시간대에 일어나는 이벤트성 패킷을 정의할 때 사용
      - Streaming의 경우 Common의 특수한 케이스로 특정시간대에 일어나지만 지속적인 패킷 다운로드가 있는 경우 사용
      - Repeatly의 경우 일정한 간격으로 발생되는 패킷이 있는 경우 사용
    - Sessions구분
      - Session_#는 일반적인 UP/DN으로 이루어진 커넥션
        - Common Task일 경우의 Session
          - Server / PortRange / UPDN / time / packet
        - Repeatedly Task일 경우의 Session
          - Server / PortRange / UPDN / time / packet / interval1 / interval2
          - interval1은 아라비아 숫자 / interval2는 시간단위
      - Streaming의 경우 Task가 Streaming일 경우 사용 되는 커넥션
        - Server / PortRange / UPDN / time / packet / Song_play_minutes / max_Playing_minutes
        - time의 내 마지막 정의 되는 소요시간이 패킷의 다운로드 시간으로 규정됨
        - Song_play_minutes는 재생 곡들의 평균적인 소요 시간 (분)
        - max_Playing_miniutes는 스트리밍의 최대 지속 시간(분) 
        - UserConfig내에 streaming을 사용하는 Useraction이 있는 경우 max_stream_time을 규정지어야함
        - 스트리밍 기능을 구현하고 싶은 경우 Session_#과 streaming을 순차적으로 사용하면 가능
      - Routine은 해당 기능이 순차적으로 어떤 세션을 가지는 지 규정.
        - 실제 패킷 생성시에는 Routine을 읽은 후에 하위 커넥션들을 찾고 이를 단위 패킷으로 구성해 나감.

3. UserConfig.json Setting
  - User의 경우 특정기기에 대한 명령이 User type을 정의함
  - Json의 구조는 "User_type : { weekday / weekend : { Task_name : { start_time, finish_time, max_trial ,(max_stream_time)
  - 개별 Task(Task_name) 를 주어진 시작시간(start_time)과 종료시간(finish_time)내 최대 몇번(max_trial)을 실행한다 라는 구조임.
  - Task가 streaming 일 경우 최대 스트리밍 시간(max_stream_time)을 지정해 주어야함.
  - Streming의 경우 최대 스트리밍 시간 만큼 작업이 지속될 수 있음.
 
 ### Excecution
 0. Set Configurations
 1. python data_gen_v2.py
 2. After Executing it, output files are in ./PacketGen/Home(1,2,3..).log
 3. (optional plotting function) python Plotting.py {logfile} {outname} {resample_seconds}
