# worship-venue-3d — 작업 인계 문서

교회 3층 다목적실(실제 공연 장소)을 웹 3D로 재현하고, **중앙 원형 무대(in-the-round)** 찬양 공연을 미리 체험하게 하는 프로젝트.
최종 목표: 설계도·현장 사진 기반 3D 공간 + 아바타로 "실제 공연장에 온 느낌". GitHub Pages로 누구나 링크로 접속.

사용자: 비개발자에 가까운 공연 기획자(찬양 콘서트 팀 대표). **한국어로, 초보자도 이해하게 설명**. 구조/이유를 먼저 설명하는 걸 선호하고, 수정 시 **부분 코드가 아니라 통째로 교체 가능한 완성 파일**을 선호.

## 현재 상태 (v0.3, 2026-11-12)
- `index.html` 한 파일에 전부 들어 있음 (Three.js r160, jsdelivr CDN importmap). 빌드 도구 없음.
- `tex/` 사진 질감 (CC0, 현장 색에 맞춰 보정): floor(ambientCG WoodFloor051 + normal/roughness), panel·perf·slat(Poly Haven oak_veneer_01), wain(Poly Haven plywood), carpet(ambientCG Carpet012 + normal).
  - 질감은 `photo()`로 비동기 로드, 실패해도 기본 색으로 렌더됨.
- `data/venue_3F_plan.json` 도면에서 뽑은 좌표 데이터(mm, 원점 X1×Y4, +X 동쪽, +Y 북쪽).
- claude.ai 아티팩트로도 게시돼 있었음(같은 내용).
- **GitHub 저장소 `choiwk/worship-venue-3d` 생성됨(비어 있음). 아직 push 안 됨.**
  - 이유: 클라우드 세션의 Claude GitHub 앱 권한이 이 저장소에 없었음. Claude Code(로컬)에서는 사용자 git 자격으로 바로 push 가능.
  - 해야 할 것: `git remote add origin https://github.com/choiwk/worship-venue-3d.git && git push -u origin main` → 저장소 Settings → Pages → Branch `main` / `/(root)` → `https://choiwk.github.io/worship-venue-3d/`
  - `reference/`는 .gitignore에 있음(현장 사진·도면·원본 프롬프트, 공개 저장소에 안 올리려고). 올릴지 사용자에게 확인할 것. `data/venue_3F_plan.json`에는 공사명(주소 포함)이 있어 공개 여부도 사용자 확인 권장.

## 좌표계 / 코드 구조 (index.html)
- `P(X, Y, h)` = 도면 좌표(m) → three: `x = X, y = h, z = -Y`.
- 맨 위 `VENUE`(건물), `SHOW`(공연 구성) 상수만 바꾸면 전체가 맞춰지게 작성.
- 섹션 순서: textures → materials → floor(+코트 라인 별도 오버레이) → gable walls → side walls(징두리/블라인드 창/목재 루버 기둥/벽등) → roof(데크, 포털 프레임, 퍼린, 브레이싱, 하이베이) → 기존 무대·박스·LED 스크린 → LIGHTING(천장등 warm, 벽등 wallPts, 스탠드 `buildStands()`) → PEOPLE(`makePerson`, 관객은 `bakePerson`→InstancedMesh) → CENTER STAGE → audience → grid → avatar → 환경맵(CubeCamera+PMREM, 조명 바뀌면 재베이크) → 후보정(UnrealBloom + 비네팅/필름 입자 ShaderPass) → controls/views/UI/loop.
- 조명 상태 `light = {high, col, stand, temp}` → `applyLights()`; 프리셋 `setPreset('show'|'rehearsal')`.
- 느린 기기: 첫 ~110프레임 평균이 느리면 후보정·그림자 끄고 pixelRatio 1. `window.__noAuto`, `__noPost`, `__noEnv` 플래그는 테스트용.
- `window.__dbg = { avatar, look(yaw,pitch) }` 테스트용 훅.

## 확정된 사실 / 사용자 결정
- 공연 장소 = 다목적실(X1~X5, 30m × 18m, 그리드 7.5m). 실내 기둥 없음, 맞배지붕(용마루 동서 방향), 기존 고정 무대는 서쪽 끝(이번 공연엔 미사용).
- 공연은 **홀 중앙**(코트 중앙 X 17.4, Y 9.0)에서 원형으로, 공연자끼리 서로 마주 봄. 관객이 사방으로 둘러쌈.
- 편성 12명: **보컬 7, 일렉 1, 베이스 1, 드럼 1, 건반 2**. 공연자 원 반지름 3.2m, 카펫 지름 9.4m(사용자가 "더 넓게" 요청해 확대).
- 조명: **좌·우 측벽 앞**(남·북)에 **7m 스탠드 조명** 2대(T바 2단 × 4구 LED 파, 참고: reference/stand_light_7m.png)가 중앙을 비춤. 벽면 조명은 **주광색 오렌지(따뜻한 색)**. 현재 기본 temp 0.2(오렌지 쪽).
- 실사 느낌 원함("애니메이션 느낌 없이").

## 열린 문제 (우선순위 순)
1. **측벽 높이 vs 7m 스탠드 충돌**: 측벽 5m·용마루 8m는 사진 비례 추정(C등급). 측벽 앞 7m 스탠드가 실제로 서려면 측벽이 더 높아야 함. 지금 코드는 `roofAt(Y) - 0.5`로 잘라 약 4.9m로 표시됨. → 사용자에게 실측 측벽 높이를 받거나, 승인받고 `VENUE.eave`를 ~7.5m로 올릴 것.
2. 사람이 마네킹 수준 — 실사감의 가장 큰 약점. 후보: Ready Player Me/Mixamo 등 GLB 인체 모델(라이선스 확인), 또는 사람을 실루엣 위주로.
3. 동쪽(뒤) 벽, X표시 구획(동남쪽 2.9 × 8.3m), 북측 통로 칸막이(W10)는 사진 없음/불일치 — 현장 확인 필요.
4. 실제 휴대폰 성능 미검증(헤드리스 SwiftShader에서만 확인).
5. 장기: 현장 LiDAR 스캔(Polycam 등)이나 가우시안 스플래팅으로 공간 자체를 사진 품질로.

## 참고 자료 (reference/, git 제외)
- `drawing_A-006_3F_roof.jpg` 설계도(3층·지붕층 평면, 1/300). `drawing_overlay_check.png` 좌표 추출 검증.
- `site-photos/` 실제 다목적실 사진 3장(무대 방향 전경, 측벽, 기둥 상부).
- `show-reference/` **다른 장소**에서 한 원형 공연 사진(구성 참고용, 공간은 우리 장소와 다름).
- `stand_light_7m.png` 사용할 스탠드 조명.
- `prompt_01_*`, `prompt_02_*` 사용자가 준 원본 요구 프롬프트.
- 도면 분석 보고서(claude.ai 문서): https://claude.ai/artifact/Cj2CDgD7HBWUup26DCZv7N

## 확인 방법
- 로컬 실행: `python3 -m http.server 8000` → http://localhost:8000 (file://로 열면 질감 로드가 막힘)
- 스크린샷 검증: `python scripts/screenshot.py` → `shots/*.png` 확인. 변경 후 항상 시점별로 눈으로 확인할 것.
