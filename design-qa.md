# Dashboard Design QA

- Source feedback videos:
  - `/Users/eric/Library/Containers/com.tencent.xinWeChat/Data/Documents/xwechat_files/wxid_6xm3vfori24k22_314b/temp/RWTemp/2026-08/b7da15e2b37c9fd6fd77857846bc92ae/6633dedef1d71cf4de927f8195676a71.mp4`
  - `/Users/eric/Library/Containers/com.tencent.xinWeChat/Data/Documents/xwechat_files/wxid_6xm3vfori24k22_314b/temp/RWTemp/2026-08/b7da15e2b37c9fd6fd77857846bc92ae/5825fd22a426d960ff93aa406d1c3778.mp4`
- Local evidence: macOS Speech transcripts and AVFoundation frames in `/tmp/dashboard-video-analysis.*`.
- Implementation screenshot: `/tmp/zx-box-modules.png`.
- Combined comparison: `/tmp/zx-box-modules-comparison.jpg`.
- Browser viewport and implementation pixels: 1280 × 720 CSS px at 1× density.
- State: Google 表格自动同步、最近 12 个月、全部职位、全部员工、KPI 模块。

## Confirmed feedback

- The main KPI page should not require a long vertical scan through unrelated charts.
- Selecting a KPI module should display only that module's own details.
- PIS, IE, Modelist, and Designer data should not be combined in one specialty chart.
- The homepage modules must follow the development order: 3D RFT, TP RFT,
  TP on time, SSS RFT, PPS RFT, and GO PROD on time.
- Role color blocks and module colors should use the same ownership palette.
- Module buttons should be large rectangular boxes, and the explanatory sentence below them should be removed.

## Findings

No actionable P0/P1/P2 findings remain.

- Fonts and typography: the existing Arial/Microsoft YaHei hierarchy remains consistent and module labels are readable.
- Spacing and layout rhythm: modules use a full-width 3 × 2 grid of 364 × 80 px rectangular controls at 1280 px; only one focused chart is rendered at a time.
- Colors and visual tokens: the Decathlon blue theme, borders, radii, and role colors remain unchanged.
- Image quality and asset fidelity: no image assets are used in the dashboard UI; Plotly charts remain crisp.
- Copy and content: the six module names match the requested development order.
- Ownership colors: Designer/3D is blue, Modelist/TP is orange, PIS/SSS and GO PROD are green, and IE/PPS is pink.

## Interaction and runtime checks

- All six KPI module buttons switched successfully.
- The sentence “一次只查看一个 KPI 模块；模块之间不再混合展示。” is absent.
- The old “岗位专项” tab and combined PIS/IE view are absent.
- Google Sheet data loaded successfully.
- Browser console warnings/errors: none.
- Python compilation, four unit tests, and `git diff --check`: passed.

## Comparison history

1. Earlier design stacked overview, RFT exception, attention, and specialty charts vertically.
2. First feedback video established that this forced users to repeatedly re-interpret context while scrolling.
3. Second feedback video established that the specialty view mixed unrelated roles and KPI types.
4. Fix: replaced the stacked overview and specialty tab with six development-stage module buttons and one focused detail panel.
5. Post-fix evidence: `/tmp/zx-box-modules.png` and browser interaction checks confirm the large rectangular controls, focused module behavior, and matching owner colors.

## Follow-up polish

No blocking follow-up polish is required for this feedback round.

final result: passed
