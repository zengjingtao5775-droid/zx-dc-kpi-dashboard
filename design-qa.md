# Dashboard Design QA

- Source visual truth:
  - `/var/folders/fz/602qzjrn7s5g1k93jp4dk9dh0000gn/T/codex-clipboard-e6a62682-46b9-4b12-971f-c4a8f8997839.jpg`
  - `/var/folders/fz/602qzjrn7s5g1k93jp4dk9dh0000gn/T/codex-clipboard-b8a6b77f-36b5-437b-a8ab-2068032eb13c.jpg`
  - `/var/folders/fz/602qzjrn7s5g1k93jp4dk9dh0000gn/T/codex-clipboard-05defefb-db2b-461d-9ae2-80b323ab3037.jpg`
  - `/var/folders/fz/602qzjrn7s5g1k93jp4dk9dh0000gn/T/codex-clipboard-538675fc-7d54-4e42-af0b-389de12c56c6.jpg`
- Implementation screenshots:
  - `/tmp/zx-dashboard-top.png`
  - `/tmp/zx-dashboard-rft.png`
- Combined comparison: `/tmp/zx-dashboard-qa-comparison.jpg`
- Browser viewport and implementation pixels: 1280 × 720 CSS px at 1× density; screenshots are 1280 × 720 px.
- Source pixels: 1920 × 1080 px for each annotation screenshot. The comparison sheet uses fitted crops because the sources include photographed browser chrome and annotations rather than a pixel-perfect mockup.
- State: Google 表格自动同步、最近 12 个月、全部职位、全部员工、管理总览。

## Findings

No actionable P0/P1/P2 findings remain.

- Fonts and typography: the existing Arial/Microsoft YaHei stack remains consistent; the personnel breakdown uses a smaller secondary line and stays readable.
- Spacing and layout rhythm: the five-card row is now four equal KPI cards; the employee count moved into the hero summary; the broad team trend section was removed as requested.
- Colors and visual tokens: existing Decathlon blue, role colors, borders, radii, and shadows remain unchanged.
- Image quality and asset fidelity: no image assets are used in the dashboard UI; Plotly charts remain crisp and legible.
- Copy and content: RFT naming is consistent across summary cards and the exception trend; target attainment is visibly capped at 100% with a short explanation.

## Focused comparison evidence

- Top summary and attainment chart: `/tmp/zx-dashboard-top.png` confirms the role breakdown, four equal cards, removed employee card, and 100% cap.
- RFT section: `/tmp/zx-dashboard-rft.png` confirms the unified RFT title and the retained per-person monthly exception detail.
- A separate focused region was not required for the removed team trend because its absence is directly confirmed between the top and RFT captures.

## Comparison history

1. P2 found: the first implementation placed all personnel counts on one long subtitle line, which could clip at a 1280 px viewport.
2. Fix: moved the personnel breakdown to a smaller second line with wrapping enabled.
3. Post-fix evidence: `/tmp/zx-dashboard-top.png` shows the full `IE 1人 / Modelist 2人 / Designer 1人 / PIS 1人` summary without clipping.

## Interaction and runtime checks

- Google Sheet data loaded successfully.
- “岗位专项” and “管理总览” tabs switched successfully.
- Browser console warnings/errors: none.
- Python compilation, four unit tests, and `git diff --check`: passed.

## Follow-up polish

No blocking follow-up polish is required for this feedback round.

final result: passed
