# 홀덤 프리플랍 드릴

**플레이: https://syup5.github.io/holdem_strategy_preflop/**

랜덤으로 생성되는 토너먼트 프리플랍 상황에서 폴드·콜·오픈 레이즈(사이즈 포함)·올인을 고르면, 전략서 이론과 13×13 레인지 차트, EV 계산으로 해설해 주는 연습 게임입니다. 설치 없이 브라우저에서 바로 실행됩니다.

## 기능

- **테이블 시각화**: 2–9명 테이블(헤즈업 포함: 버튼이 SB를 겸하는 규칙과 전용 레인지 적용), 좌석별 행동 순서 번호·포지션·스택(BB/칩)·액션 상태, 딜러 버튼, 베팅 칩, 팟
- **스택 정보**: 내 스택, 유효 스택, M-비율(해링턴 존), 테이블 총 칩·평균·내 비중·순위, 콜 금액
- **상황 4종**: 오픈 기회(폴드된 팟) · 레이즈 상대(콜/3벳/올인) · 올인 상대(콜/폴드) · 림퍼 상대(아이소 레이즈)
- **채점**: 최선 / 허용 / 실수 3단계, 액션과 레이즈 사이즈를 따로 판정
- **설정**: 모드(이론/홀덤펍), 인원(랜덤, 9·8·7·6·5·4·3·2명), 스택 깊이(숏/미들/딥 토글, 여러 개를 켜면 섞어서 출제), BB 앤티 유무, 상황 유형(오픈/레이즈/올인/림퍼 토글), 출제 난이도. 성적은 브라우저(localStorage)에 저장
- **홀덤펍 모드**: 카드 확률은 그대로 두고 상대 행동만 펍 성향으로 바꿔 채점. 테이블 성향(콜 많음/폴드 많음)과 대회 구간(리바이/일반/버블·시상권)을 고름
  - 숏스택 푸시·리스틸·올인 콜: 상대가 정해진 범위로 콜·푸시한다고 보고 EV 재계산 (콜 많음 = 아무 페어·아무 에이스·브로드웨이 약 26%, 폴드 많음 = 77+·AJ+ 약 8%, 리바이 구간은 한 단계 더 루즈)
  - 딥스택: 얼리 포지션 약한 오프수트·순수 스틸·블러프 3벳 축소, 앞자리 오픈에 오프수트 하이카드 콜 제외, 스몰 페어·수딧 커넥터 콜 기준 완화(유효 30BB+)
  - 사이즈: 오픈 2.5~3BB(SB 3~4BB), 밸류 3벳 약 4배, 아이소 4BB(포지션 없으면 5BB) + 림퍼당 1BB. 권장 사이즈가 스택의 40~45%를 넘으면 올인
  - 버블·시상권: ICM 근사로 올인 콜 필요 에퀴티 +8%p, 푸시는 EV가 유효 스택의 5% 이상일 때만, 경계 핸드는 폴드
  - 출제: 오픈 3~4BB, 림프 상황과 림퍼 수 증가, 숏·미들 스택 위주
- **단축키**: `F` 폴드 · `C` 콜/체크 · `1–4` 레이즈 · `A` 올인 · `Space` 다음
- **휴대폰 화면**: 테이블·내 핸드·액션 버튼이 한 화면(375×667 기준)에 들어오도록 배치. 설정은 `설정` 버튼으로 접고 펼치며, 답하면 버튼 아래 결과 요약 줄([해설] [다음])이 나타남
- **부록 A — 포지션별 오픈 레인지 표 + 오픈 레인지 암기 게임**: 9인 기준 자리·6인 대응 자리·뒤 인원·오픈 %(코어/경계 포함/가중)·숏스택 내쉬 푸시 %(10·15·20BB), 행을 누르면 13×13 차트와 레인지 표기. 게임은 "이 자리에서 이 핸드를 오픈? (오픈/경계/폴드)"와 "이 자리 오픈 %는?" 두 유형
- **부록 B — 핸드 퍼센트 암기표 + 핸드 퍼센트 암기 게임**: 랜덤 핸드 상대 올인 에퀴티 순위 기준 "상위 X%" 히트맵, 상위 5~50% 레인지 표, 핸드의 상위 % 구간 맞히기 게임. 게임 해설에도 매번 "핸드 순위: 상위 X%" 표시
- 두 암기 게임은 점수를 따로 기록하고, 기본적으로 문제를 푸는 동안 참고표를 흐리게 가립니다(체크 해제 가능)

## 전략 근거

- **딥 스택(25BB 초과)**: 포지션별 오픈·디펜스 레인지는 100BB 기준 GTO 솔버 결과를 단순화한 근사 차트입니다(경계 핸드는 두 선택 모두 허용).
- **숏 스택**: 169×169 프리플랍 올인 에퀴티 행렬(매치업당 약 24,000회 몬테카를로)로 chipEV 내쉬 균형 푸시/폴드 차트를 직접 계산했습니다(동일 스택, 오버콜 무시, 카드 제거 효과 반영). 리스틸·올인 콜 판단은 같은 행렬로 실시간 EV를 계산합니다.
- 모든 판단은 chipEV 기준입니다. 버블·파이널 테이블처럼 ICM 압력이 큰 상황에서는 더 타이트해야 합니다.

## 파일

| 파일 | 설명 |
|---|---|
| `index.html` | GitHub Pages용 단일 페이지 (빌드 결과물) |
| `261025_233500_holdem_preflop_drill.html` | 게임 원본 (Claude Artifact 형식) |
| `261025_232000_precompute_preflop.py` | 에퀴티 행렬·내쉬 차트 계산, 데이터 삽입, Pages 빌드 |
| `261025_232000_preflop_data.json` | HTML에 삽입되는 데이터 (에퀴티 행렬 + 푸시 차트) |
| `261025_232000_equity169.npy` | 169×169 에퀴티 행렬 |

## 다시 빌드하기

```bash
pip install numpy eval7
python 261025_232000_precompute_preflop.py equity   # 에퀴티 행렬 (8코어 약 4분)
python 261025_232000_precompute_preflop.py nash     # 내쉬 푸시/폴드 차트 (약 6분)
python 261025_232000_precompute_preflop.py inject 261025_233500_holdem_preflop_drill.html
python 261025_232000_precompute_preflop.py pages 261025_233500_holdem_preflop_drill.html index.html
```

## 참고 문헌

- Dan Harrington & Bill Robertie, *Harrington on Hold'em, Vol. II: The Endgame*, Two Plus Two, 2005 — M-비율과 존 시스템 ([링크](https://en.wikipedia.org/wiki/Harrington_on_Hold_%27em))
- Bill Chen & Jerrod Ankenman, *The Mathematics of Poker*, ConJelCo, 2006 — 잼-오어-폴드 게임 ([링크](https://www.pokernews.com/news/2006/12/poker-book-review-mathematics-poker-3456.htm))
- Lee Nelson, Tysen Streib & Steven Heston, *Kill Everyone*, Huntington Press, 2007 (2판 2009) — 폴드 에퀴티와 균형 기반 올인 전략 ([링크](https://huntingtonpress.com/kill-everyone/))
- Michael Acevedo, *Modern Poker Theory*, D&B Poker, 2019 — GTO 기반 프리플랍 레인지 ([링크](https://vaski.finna.fi/Record/vaski.4218306?lng=en-gb))
- David Sklansky & Ed Miller, *No Limit Hold 'em: Theory and Practice*, Two Plus Two, 2006 — 스택 크기 조정과 임플라이드 오즈 ([링크](https://www.pokernews.com/news/2007/04/poker-book-theory-practice-sklansky-3722.htm))
