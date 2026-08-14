# Dashboard Design QA

- Live data source: Google Sheet `ZX DC dashboard KPI & data`
- Active worksheet: `8.14 DATABASE for Dashboard`
- Latest feedback evidence:
  - `/Users/eric/Library/Containers/com.tencent.xinWeChat/Data/Documents/xwechat_files/wxid_6xm3vfori24k22_314b/temp/RWTemp/2026-08/b7da15e2b37c9fd6fd77857846bc92ae/1267f9058bc700e8dde185addfab02eb.mp4`
  - `/Users/eric/Library/Containers/com.tencent.xinWeChat/Data/Documents/xwechat_files/wxid_6xm3vfori24k22_314b/temp/RWTemp/2026-08/b7da15e2b37c9fd6fd77857846bc92ae/491187727852e1bd4e3c33391563b4e4.mp4`
- Video analysis: local macOS Speech and AVFoundation only; no upload.
- Browser viewport: 1280 × 720 CSS px at 1× density.

## Confirmed requirements

- Read the new dashboard database instead of the legacy `KPI database` sheet.
- Support the source columns `JOB`, `NAME`, `KPI`, followed by monthly columns.
- Display the development-file order as Modelist, IE, Designer, PIS. Source role `ME` is presented as `IE` in the UI.
- Keep all KPI modules as rectangular cards in one desktop row and use the owner-role color.
- Module order:
  1. TP RFT
  2. TP ON TIME
  3. MARKER RFT
  4. MARKER ON TIME
  5. SOT RFT
  6. SOT ON TIME
  7. 3D RFT
  8. SSS RFT
  9. SSS ON TIME
  10. PPS RFT
  11. PPS ON TIME
- Split TP charts by employee so Mengli Jiang and Jiao Chen never cover each other's trend lines.
- Treat `NA` or `N/A` as not applicable: do not calculate it, do not count it as invalid data, and display no KPI value.
- Keep a fully Chinese interface in Chinese mode and a fully English interface in English mode.
- Do not fabricate values for blank source cells.

## Source verification on 2026-08-14

- Worksheet selected: `8.14 DATABASE for Dashboard`
- Source roster: 5 employees across 4 source roles.
- Valid KPI records currently present:
  - Louis Diao, 3D RFT, 2026/01: 100%
  - Louis Diao, 3D RFT, 2026/02: 100%
  - Jiao Chen, TP BOM RFT, 2026/02: 50%
- All other KPI-month cells are currently blank and therefore appear as `—`/no data.
- The loader also supports the earlier two-row year/month header format.

## Verification status

- Python compilation: passed.
- Six unit tests: passed, including single-row, two-row, and `NA` handling.
- `git diff --check`: passed.
- Local browser at 1280 × 720: all 11 cards fit one row without horizontal clipping.
- Chinese/English interaction and KPI module switching: passed.
- Browser console warnings/errors: none.
- Production refresh verification: passed; the live app loaded the new roster and the 50% TP record after a forced Google refresh.

final result: passed
