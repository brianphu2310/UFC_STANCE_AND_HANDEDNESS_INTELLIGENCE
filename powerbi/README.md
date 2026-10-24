# Stance Intelligence trong Power BI

Gói này để dựng lại app dưới dạng báo cáo Power BI, theo bản xem trước 5 trang (Home, Overview,
Explorer, Stance lab, Build a fighter). Cần Power BI Desktop (Windows). Dựng mất khoảng 1–2 giờ.

| File | Dùng để |
|---|---|
| `data/fighters.csv` | Bảng chính: mỗi dòng một võ sĩ (stance, tay, chân, thành tích, thể hình, phong cách) |
| `data/skills.csv` | Mỗi dòng một võ sĩ × một kỹ năng: giá trị thật và percentile so với 117 võ sĩ |
| `data/stance_tests.csv` | 5 phép so sánh của Stance lab: chênh lệch, khoảng tin cậy 95%, p, Cohen's d |
| `data/gear.csv` | Danh mục gear và khoảng giá AUD |
| `stance_intelligence_theme.json` | Theme màu, font, khung của app |
| `measures.dax` | Các measure DAX |
| `backgrounds/*.jpg` | Ảnh nền 1280×720 cho từng trang: ảnh trận đấu phủ tối 82%, banner và tiêu đề |

Tạo lại dữ liệu và ảnh nền: `python scripts/build_powerbi_pack.py <đường dẫn font Big Shoulders Display .ttf>`.

## 1. Dữ liệu và theme

1. **Get data → Text/CSV**, nạp cả 4 file trong `data/`. `champion` để kiểu True/False, `win_rate` kiểu số thập phân.
2. **Model view**: nối `fighters[fighter]` → `skills[fighter]` (một-nhiều).
3. **View → Themes → Browse for themes**, chọn `stance_intelligence_theme.json`.
4. **Modeling → New measure**: tạo lần lượt các measure trong `measures.dax`.
5. Cho trang Explorer: **Modeling → New table** hai lần, `Fighter A = DISTINCT ( fighters[fighter] )` và `Fighter B = DISTINCT ( fighters[fighter] )`. Hai bảng này **không nối** với bảng nào.

## 2. Mỗi trang

Mọi trang: **Format page → Canvas settings** để 16:9 (1280×720); **Canvas background → Image**, chọn
ảnh trong `backgrounds/`, *Image fit* = Fit, *Transparency* = 0% (ảnh đã phủ tối sẵn). Vùng 0–68 px
trên cùng để trống cho thanh nút; dải banner nằm ở 68–160 px.

**Thanh nút chuyển trang** (làm một lần ở trang Home rồi copy sang các trang):
**Insert → Buttons → Navigator → Page navigator**, đặt ở góc trên, cao 40 px. Trong Format: trang đang
mở *Fill* = `#C8102E`, chữ trắng; các trang khác viền `#2E2E30`.

| Trang | Ảnh nền | Visual |
|---|---|---|
| Home | `01_home.jpg` | 4 **Card**: `[Fighters]`, `[Countries]`, `[Southpaw share]`, `[Left-handed share]`. 1 **Matrix** "Tale of the tape": hàng là tên chỉ số, hai cột `[Orthodox win rate]`, `[Southpaw win rate]` (thêm Champions, Median reach theo cùng cách lọc stance) |
| Overview | `02_overview.jpg` | **Slicer** dropdown: weight_class, stance, hand; slicer danh sách: continent. 4 **Card**. **Donut** stance theo `[Fighters]`. **Clustered bar** top 8 country (Filters: Top N = 8 theo `[Fighters]`). **Clustered bar** stance_hand theo `[Mean win rate]`. **Clustered column** debut_year theo `[Fighters]`. Thêm **Filled map** theo country nếu muốn có bản đồ |
| Explorer | `03_explorer.jpg` | **Slicer** dropdown `'Fighter A'[fighter]` và `'Fighter B'[fighter]` (Single select). 2 **Multi-row card** cho thông số mỗi người (lọc theo tên đã chọn). **Clustered bar** "butterfly": trục Y `skills[skill]`, giá trị `[A percentile (left)]` (đỏ) và `[B percentile]` (xanh), Overlap 100%. **Card** `[Stance geometry]`. **Table** fighter, stance, win_rate sắp theo popularity_index |
| Stance lab | `04_stance_lab.jpg` | **Text box** kết luận. **Error bars**: Clustered bar `stance_tests[comparison]` theo `diff`, bật *Error bars* với ci_low / ci_high. **Table** n_a, n_b, diff, ci_low, ci_high, welch_p, d |
| Build a fighter | `05_build_a_fighter.jpg` | **Numeric range slicer** (Modeling → New parameter → Numeric range) cho chiều cao, cân nặng, sải tay. Slicer tay, chân, style. **Table** võ sĩ gần nhất (sắp theo độ chênh chiều cao + sải tay so với tham số). **Table** gear từ `gear.csv` |

## 3. Power BI làm được và không làm được

Làm được: ảnh nền đứng yên mỗi trang, biểu đồ, bộ lọc, thanh nút chuyển trang, theme màu.
Không làm được như bản web: hình nộm 3D, intro video, nền ảnh tự đổi, hiệu ứng khi cuộn và đổi
tab, và phần gợi ý stance, lộ trình tập, gear theo từng người (logic Python; trong Power BI chỉ mô
phỏng được một phần bằng slicer và DAX).

Ảnh nền dùng ảnh báo chí có bản quyền (Topuria, Holloway, McGregor, Aldo, Oliveira), chỉ cho bài thuyết trình trên lớp.
