# Dashboard Design QA

- Live data source: Google Sheet `ZX DC dashboard KPI & data`
- Active worksheet: `8.14 DATABASE for Dashboard`
- Latest feedback evidence:
  - `/var/folders/fz/602qzjrn7s5g1k93jp4dk9dh0000gn/T/codex-clipboard-6f7c1262-29e6-4893-8210-a366f2c48e36.png`
  - `/var/folders/fz/602qzjrn7s5g1k93jp4dk9dh0000gn/T/codex-clipboard-1ee76840-317c-48d9-8561-f7862ce6cc68.png`
  - `/Users/eric/Library/Containers/com.tencent.xinWeChat/Data/Documents/xwechat_files/wxid_6xm3vfori24k22_314b/temp/RWTemp/2026-08/b7da15e2b37c9fd6fd77857846bc92ae/1267f9058bc700e8dde185addfab02eb.mp4`
  - `/Users/eric/Library/Containers/com.tencent.xinWeChat/Data/Documents/xwechat_files/wxid_6xm3vfori24k22_314b/temp/RWTemp/2026-08/b7da15e2b37c9fd6fd77857846bc92ae/491187727852e1bd4e3c33391563b4e4.mp4`
  - `/Users/eric/Library/Containers/com.tencent.xinWeChat/Data/Documents/xwechat_files/wxid_6xm3vfori24k22_314b/temp/RWTemp/2026-08/b7da15e2b37c9fd6fd77857846bc92ae/85b1c9518cc213994b748297ccdabdbe.mp4`
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
- Split TP charts into fixed left/right employee panels so Jiao Chen and Mengli Jiang never share one chart. Keep an employee's panel visible with `—` when their data has not been entered yet.
- MARKER belongs to Modelist: both MARKER cards use the same orange ownership color as TP, while SOT remains purple for ME/IE.
- Split MARKER RFT and MARKER ON TIME into the same fixed Jiao Chen / Mengli Jiang left-right panels.
- Treat `NA` or `N/A` as not applicable: do not calculate it, do not count it as invalid data, and display no KPI value.
- Keep a fully Chinese interface in Chinese mode and a fully English interface in English mode.
- Do not fabricate values for blank source cells.

## Source verification on 2026-08-14

- Worksheet selected: `8.14 DATABASE for Dashboard`
- Source roster: 5 employees across 4 source roles.
- Latest export: 19 KPI rows and 43 valid KPI-month records through 2026/07.
- MARKER rows now belong to Jiao Chen and Mengli Jiang under Modelist; their current monthly values are blank and correctly display `—` without borrowing TP data.
- The loader also supports the earlier two-row year/month header format.

## Verification status

- Python compilation: passed.
- Six unit tests: passed, including single-row, two-row, and `NA` handling.
- `git diff --check`: passed.
- Local browser at 1280 × 720: all 11 cards fit one row without horizontal clipping.
- Chinese/English interaction and KPI module switching: passed.
- Browser console warnings/errors: none.
- Screenshot comparison passed: MARKER RFT and MARKER ON TIME are orange, SOT remains purple, and both MARKER modules show separate Jiao Chen / Mengli Jiang panels.
- Production refresh verification: passed; the live app loaded the new roster and the 50% TP record after a forced Google refresh.
- Production MARKER verification: passed; both MARKER cards are orange, both employee panels render independently, and the browser console has no warnings or errors.

final result: passed
