# Dashboard Design QA

- Source feedback videos:
  - `/Users/eric/Library/Containers/com.tencent.xinWeChat/Data/Documents/xwechat_files/wxid_6xm3vfori24k22_314b/temp/RWTemp/2026-08/b7da15e2b37c9fd6fd77857846bc92ae/6633dedef1d71cf4de927f8195676a71.mp4`
  - `/Users/eric/Library/Containers/com.tencent.xinWeChat/Data/Documents/xwechat_files/wxid_6xm3vfori24k22_314b/temp/RWTemp/2026-08/b7da15e2b37c9fd6fd77857846bc92ae/5825fd22a426d960ff93aa406d1c3778.mp4`
  - `/Users/eric/Library/Containers/com.tencent.xinWeChat/Data/Documents/xwechat_files/wxid_6xm3vfori24k22_314b/temp/RWTemp/2026-08/b7da15e2b37c9fd6fd77857846bc92ae/7868efa7e12c107efbafaefeecc12582.mp4`
  - `/Users/eric/Library/Containers/com.tencent.xinWeChat/Data/Documents/xwechat_files/wxid_6xm3vfori24k22_314b/temp/RWTemp/2026-08/b7da15e2b37c9fd6fd77857846bc92ae/fd03a3fa9722ff2d92fd066742d574f9.mp4`
  - `/Users/eric/Library/Containers/com.tencent.xinWeChat/Data/Documents/xwechat_files/wxid_6xm3vfori24k22_314b/temp/RWTemp/2026-08/b7da15e2b37c9fd6fd77857846bc92ae/03ffa84b257b6799e634d3154ffc06d1.mp4`
  - `/Users/eric/Library/Containers/com.tencent.xinWeChat/Data/Documents/xwechat_files/wxid_6xm3vfori24k22_314b/temp/RWTemp/2026-08/b7da15e2b37c9fd6fd77857846bc92ae/46104531ec6914bbbfb4d17a5b4c1743.mp4`
  - `/Users/eric/Library/Containers/com.tencent.xinWeChat/Data/Documents/xwechat_files/wxid_6xm3vfori24k22_314b/temp/RWTemp/2026-08/b7da15e2b37c9fd6fd77857846bc92ae/60a038734a9fd0df0b76779666c340fc.mp4`
- Local evidence: macOS Speech transcripts, AVFoundation frames, and contact sheets in `/tmp/dashboard-video-three`, `/tmp/dashboard-video-four`, and `/tmp/dashboard-video-five`.
- Browser viewport and implementation pixels: 1280 × 720 CSS px at 1× density.
- State: Google 表格自动同步、最近 12 个月、全部职位、全部员工、KPI 模块。

## Confirmed feedback

- The main KPI page should not require a long vertical scan through unrelated charts.
- Selecting a KPI module should display only that module's own details.
- PIS, IE, Modelist, and Designer data should not be combined in one specialty chart.
- The homepage modules must follow the development order: 3D RFT, TP RFT,
  TP on time, SSS RFT, PPS RFT, and GO PROD on time.
- Role color blocks and module colors should use the same ownership palette.
- Module buttons should be rectangular boxes in one desktop row, and the explanatory sentence below them should be removed.
- Filters should not occupy the default first-screen view, but remain available when needed.
- The dashboard name should use `DC`, with English as the primary language and smaller Chinese support text.
- Header role order should follow the confirmed development-file sequence: Modelist, IE, Designer, PIS, then ME.
- The redundant target card and blank latest-month card should be removed from each focused module.
- The data-instructions tab should be removed; retain only KPI Dashboard and Performance Detail.
- A visible Chinese/English switch should replace the mixed-language interface; each mode must use one language consistently.
- PPS RFT belongs to PIS and must use the PIS green ownership color.
- ME requires four focused modules: MARKER RFT, MARKER ON TIME, SOT RFT, and SOT ON TIME.
- Period controls must visibly change the selected time window even when some months have no source data.
- Each KPI module box should show its period result directly so users can read the headline value without opening the trend chart.
- Role order must follow the development-file handoff sequence: Modelist, IE, Designer, PIS, then ME.
- TP on-time must be shown as a percentage, not an average late-submission count.

## Findings

No actionable P0/P1/P2 findings remain.

- Fonts and typography: English is primary in the title, navigation, filters, and focused summary; Chinese is retained as compact support text.
- Spacing and layout rhythm: modules remain in one full-width row; the sidebar is collapsed by default and the three large metric cards are replaced with one compact period summary.
- Colors and visual tokens: the Decathlon blue theme, borders, radii, and role colors remain unchanged.
- Image quality and asset fidelity: no image assets are used in the dashboard UI; Plotly charts remain crisp.
- Copy and content: the six module names match the requested development order.
- Ownership colors: Designer/3D is blue, Modelist/TP is orange, PIS/SSS and GO PROD are green, and IE/PPS is pink.
- Header ownership order now matches the module color sequence.
- The language switch is positioned above the hero panel. Chinese mode localizes navigation, filters, role names, module names, summaries, chart labels, tooltips, and tables; English mode localizes the same surfaces and translates known source KPI names.
- The KPI row now contains ten boxes in one desktop row. PPS uses PIS green; the four ME boxes use a dedicated purple ownership color and are ready to populate when ME rows are added to the source sheet.
- Module boxes now show the selected-period average: percentages for rate KPIs, average count for the TP exception KPI, and an em dash when no matching source data exists.
- Last 12 Months now displays the full 12-month window, Year to Date starts in January, and Custom uses its selected endpoints; missing months remain available on the chart axis.

## Interaction and runtime checks

- All six KPI module buttons switched successfully.
- The sentence “一次只查看一个 KPI 模块；模块之间不再混合展示。” is absent.
- The old “岗位专项” tab and combined PIS/IE view are absent.
- Google Sheet data loaded successfully.
- Browser console warnings/errors: none.
- Python compilation, four unit tests, and `git diff --check`: passed.
- Local browser verification confirmed the collapsed filter panel, two-tab navigation, six single-row modules, compact period summary, and removal of the Target card.
- Language QA confirmed that the English interface contains no Chinese text except the `中文` switch label, including the TP on-time exception module; Chinese and English performance-detail views also load successfully.
- Current Google Sheet verification (2026-08-14) found no ME rows and no PIS KPI containing PPS, so those new modules correctly show an empty-data message instead of borrowing unrelated IE or PIS metrics.
- Browser interaction QA confirmed Last 12 Months `2025/08–2026/07`, Year to Date `2026/01–2026/07`, and a visible Custom month-range control.
- Header and role-filter ordering are fixed to the development sequence rather than alphabetical source-row order.
- TP on-time card compliance is calculated as employee-month records with no more than two late submissions divided by all recorded employee-months; the detailed chart continues to show raw counts and reasons.

## Comparison history

1. Earlier design stacked overview, RFT exception, attention, and specialty charts vertically.
2. First feedback video established that this forced users to repeatedly re-interpret context while scrolling.
3. Second feedback video established that the specialty view mixed unrelated roles and KPI types.
4. Fix: replaced the stacked overview and specialty tab with six development-stage module buttons and one focused detail panel.
5. Post-fix evidence: `/tmp/zx-one-row-boxes.png` and browser interaction checks confirm the single-row rectangular controls, focused module behavior, and matching owner colors.

## Follow-up polish

No blocking follow-up polish is required for this feedback round.

final result: passed
