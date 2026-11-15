# INDUSTRY DESK · 기자 워크데스크

## 배포 (GitHub Pages, 무료)
1. GitHub에서 새 **공개** 저장소 `industry-desk`를 만든다. 이 폴더의 **파일과 `.github/workflows/daily.yml`을 포함한 전체 내용**을 저장소 루트에 올린다. (ZIP 파일을 그대로 올리면 작동하지 않음.)
2. 저장소 **Settings → Pages → Build and deployment → Deploy from a branch → `main` / `(root)` → Save**.
3. 공개 주소는 `https://<GitHub 사용자명>.github.io/industry-desk/` 형식. 정확한 주소는 Pages 설정에서 확인.
4. **Actions → Daily 7 AM industry desk update → Run workflow**를 한 번 눌러 최초 뉴스 데이터를 생성한다.
5. 이후 매일 **한국시간 오전 7시**에 GitHub Actions가 RSS 뉴스 헤드라인을 수집, JSON에 저장한다. 단, GitHub 예약 실행은 지연·누락 가능성이 있어 정확히 07:00 보장 불가. 웹페이지는 새로고침할 때 최신 JSON을 읽는다.

## 데이터의 한계 (중요)
- 별도 뉴스 API 키 없이 **Google News RSS 검색 결과의 제목, 언론사, 게시 시간, 원문 링크**를 수집한다. 제목만으로 본문 요약이나 기업 영향을 **사실처럼 생성하지 않는다**.
- `국회 일정` 카테고리의 자동 결과는 **일정 관련 보도/공지 검색**이지 확정 일정표가 아니다. 홈페이지에서는 '확인 필요'로 표시한다.
- 공식 자료에서 확인한 일정만 `data/schedule_manual.json`에 다음 형식으로 추가하면 '확정 일정'에 노출된다:
  ```json
  [{"title":"산업통상자원중소벤처기업위원회 전체회의", "starts_at":"2026-11-16T10:00:00+09:00", "place":"국회", "source_url":"https://...", "verified_on":"2026-11-15", "committee":"산자위"}]
  ```
- 공식 국회 의사일정과 발의 법안의 완전한 자동 연동은 국회 공식 데이터 API 및 인증키/접근 가능한 게시 자료가 추가로 필요하다.
- GitHub Pages는 정적 사이트: 저장 기사와 취재 메모는 **해당 브라우저에만 저장**. 비공개 취재원 메모나 민감 정보는 공개 저장소에 넣지 말 것.
- GitHub Actions는 저장소 비활성 상태가 오래 지속되면 예약 워크플로가 비활성화될 수 있음.
