# PHÂN TÍCH MÔ TẢ VÀ CHẨN ĐOÁN
## Đề tài: Cải thiện tỷ lệ đúng giờ của Delta Air Lines
Thực hiện: Nguyễn Minh Quân | Nguồn dữ liệu: Kaggle usdot/flight-delays (2015), lọc riêng Delta Air Lines

---

## Câu hỏi nghiên cứu

*"Các yếu tố về thời gian, sân bay khởi hành, tuyến bay và nguyên nhân vận hành ảnh hưởng như thế nào đến tình trạng trễ chuyến của Delta Air Lines, và Delta nên ưu tiên cải thiện ở đâu để nâng cao tỷ lệ đúng giờ trước mùa cao điểm?"*

Câu hỏi này được trả lời qua 4 lớp phân tích theo trình tự: Mô tả (chuyện gì đang xảy ra), Chẩn đoán (vì sao xảy ra), Dự đoán (chuyến nào có nguy cơ trễ) và Chỉ định (nên làm gì). Phần dưới đây trình bày hai lớp đầu tiên: Mô tả và Chẩn đoán, áp dụng riêng cho Delta Air Lines.

---

## 1. Dữ liệu và phạm vi phân tích

Dữ liệu sử dụng là `flights_DL.csv`, được lọc riêng các chuyến của Delta Air Lines (mã `DL`) từ bộ dữ liệu chuyến bay nội địa Hoa Kỳ năm 2015, cùng schema với dữ liệu gốc. Biến mục tiêu `IS_DELAYED` được xác định trực tiếp từ `ARRIVAL_DELAY`: bằng 1 nếu trễ từ 15 phút trở lên (chuẩn US DOT), bằng 0 nếu đúng giờ, và không xác định nếu không có `ARRIVAL_DELAY` (chủ yếu là chuyến bị hủy).

Toàn bộ phân tích chỉ xét các chuyến không bị chuyển hướng (`DIVERTED = 0`) và không bị hủy (`CANCELLED = 0`). Trong 875.881 chuyến ban đầu, có 1.782 chuyến bị chuyển hướng và 3.824 chuyến bị hủy, đều được loại khỏi phân tích; còn lại 870.275 chuyến hoàn thành và có đầy đủ thông tin để tính tỷ lệ trễ.

---

## 2. Phân tích Mô tả (Descriptive Analysis)

*Trình tự trình bày: Tổng quan → Sân bay nào? → Tuyến nào?*

Trên tập dữ liệu đủ điều kiện (870.275 chuyến), tỷ lệ chuyến bay của Delta bị trễ từ 15 phút trở lên là 13,6%. Tỷ lệ đúng giờ dao động theo mùa: thấp nhất vào tháng 2 (80,4% đúng giờ) và cao nhất vào tháng 10 (92,2% đúng giờ), chênh lệch 11,8 điểm phần trăm.

Xét theo sân bay khởi hành, trong 157 sân bay Delta khai thác, có 101 sân bay đạt ngưỡng tối thiểu 1.000 chuyến/năm được xem là sân bay có sản lượng khai thác lớn theo ngưỡng nghiên cứu (không phải định nghĩa hub chính thức theo mạng bay). Trong nhóm này, **LGA (LaGuardia, New York)** có tỷ lệ trễ cao nhất: 21,1%, cao hơn trung bình toàn Delta 7,6 điểm phần trăm (chênh lệch tính trên số liệu chưa làm tròn). Đáng chú ý, các sân bay đứng đầu nhóm rủi ro cao đều tập trung ở khu vực Đông Bắc và các thành phố lớn có mật độ không lưu cao (LGA, JFK, BOS, ORD), phản ánh áp lực từ hạ tầng không lưu khu vực này.

Ở cấp độ tuyến bay, sau khi loại 659 quan sát có ít nhất một mã sân bay không hợp lệ (0,08% số quan sát trong tập đủ điều kiện — tỷ lệ rất thấp sau khi dữ liệu gốc được rà soát lại mã sân bay), dữ liệu còn lại được dùng để xây dựng các tuyến bay thực tế; khi tính tỷ lệ trễ theo tuyến, chỉ các chuyến có `IS_DELAYED` hợp lệ mới được đưa vào mẫu số. Từ 970 tuyến thật, có 462 tuyến đạt ngưỡng tối thiểu 500 chuyến. Tuyến rủi ro cao nhất là **SFO–LAX** (San Francisco – Los Angeles): 43,8% trên 1.570 chuyến — cao vượt trội so với phần còn lại. Đặc biệt, chiều ngược lại **LAX–SFO** cũng lọt vào vị trí thứ 2 (35,4% trên 1.569 chuyến), cho thấy cả hai chiều của cùng một cặp thành phố đều có rủi ro cao. Nguyên nhân cụ thể của hiện tượng này cần được kiểm tra thêm theo thời tiết, lịch khai thác và các yếu tố vận hành — dữ liệu hiện có chưa đủ để kết luận nguyên nhân.

### Nhận xét từng biểu đồ

**Biểu đồ 1 — Tỷ lệ đúng giờ theo tháng (Line chart):** Tỷ lệ đúng giờ thấp nhất tháng 2 (80,4%) và cao nhất tháng 10 (92,2%), chênh lệch 11,8 điểm %.

**Biểu đồ 2 — Tỷ lệ trễ theo sân bay khởi hành, Top 15 sân bay sản lượng cao (Bar chart):** LGA có tỷ lệ trễ cao nhất (21,1%), vượt trung bình toàn Delta 7,6 điểm % (tính trên số liệu chưa làm tròn); các sân bay khu vực Đông Bắc (LGA, JFK, BOS) chiếm phần lớn nhóm rủi ro cao nhất.

**Biểu đồ 3 — Route Risk: khối lượng khai thác so với tỷ lệ trễ (Scatter chart):** Trong 462 tuyến đạt ngưỡng thống kê, SFO–LAX rủi ro cao nhất (43,8% trên 1.570 chuyến), theo sau bởi chính chiều ngược LAX–SFO (35,4%) — hai chiều của cùng một cặp thành phố cùng lọt top 2.

---

## 3. Phân tích Chẩn đoán (Diagnostic Analysis)

*Trình tự trình bày: Nguyên nhân gì? → Khi nào? → Nghiêm trọng thế nào?*

Phân tích 5 nhóm nguyên nhân trễ cho thấy đối với riêng Delta, nhóm nguyên nhân liên quan đến hãng hàng không (`AIRLINE_DELAY`) chiếm tỷ trọng lớn nhất: 37,4% tổng phút trễ, tiếp theo là trễ dây chuyền do máy bay đến trễ chuyến trước (`LATE_AIRCRAFT_DELAY`, 29,5%) và hệ thống không lưu quốc gia (`AIR_SYSTEM_DELAY`, 24,6%). Thời tiết chiếm 8,3% và an ninh không đáng kể (0,1%). Đây là điểm khác biệt so với bức tranh chung của toàn ngành, nơi trễ dây chuyền thường là nguyên nhân lớn nhất — với Delta, nguyên nhân được ghi nhận cho hãng bay lại nổi bật hơn. Dữ liệu không nêu rõ thành phần cụ thể của `AIRLINE_DELAY` (ví dụ bảo trì, nhân sự...), nên nhóm không suy diễn thêm ngoài phạm vi được dataset ghi nhận.

Phân tích theo khung giờ và ngày trong tuần (dựa trên ma trận giờ×ngày ở Biểu đồ 5) cho thấy Delta không khai thác chuyến vào các khung 2h-4h sáng. Trong các khung giờ hoạt động, tỷ lệ trễ thấp nhất vào sáng sớm (5h-8h, dưới 10%) và có xu hướng tăng dần trong ngày, đạt đỉnh tại khung 18h với tỷ lệ trễ gộp 20,2% (tính bằng tổng số chuyến trễ chia tổng số chuyến đủ điều kiện tại khung giờ đó, không phải trung bình đơn giản của 7 tỷ lệ theo ngày). Để kiểm chứng xu hướng tăng theo giờ, nhóm tính thêm trung bình phút `LATE_AIRCRAFT_DELAY` — chỉ tính trên các chuyến đã trễ, không phải tỷ lệ trễ — theo giờ khởi hành: con số này tăng từ khoảng 1,7-4,6 phút trong khung 5h-8h lên đỉnh 28,7 phút lúc 18h, phù hợp với giả thuyết trễ dây chuyền — dù đây vẫn là quan hệ tương quan quan sát được, chưa kiểm soát các yếu tố gây nhiễu khác nên không khẳng định là quan hệ nhân quả tuyệt đối. Ngoài ra, Thứ Năm nổi bật với tỷ lệ trễ cao hơn hẳn các ngày khác vào khung chiều-tối (ví dụ 25,1% lúc 18h so với 15,7-21,0% ở các ngày còn lại), trong khi Thứ Bảy có tỷ lệ trễ thấp nhất ở hầu hết các khung giờ.

Xét mức độ nghiêm trọng khi đã trễ theo tháng, tháng 5 có median phút trễ cao nhất (40 phút), trong khi tháng 10 thấp nhất (30 phút). Đáng chú ý, tháng có tần suất trễ cao nhất (tháng 2, 80,4% đúng giờ) không trùng với tháng có mức độ trễ nghiêm trọng nhất (tháng 5) — cho thấy tần suất và mức độ nghiêm trọng của trễ chuyến là hai khía cạnh độc lập, cần được theo dõi riêng biệt khi lập kế hoạch nguồn lực dự phòng. Tháng 10 nhất quán ở cả hai chiều: vừa có tỷ lệ đúng giờ cao nhất, vừa có mức độ trễ nhẹ nhất khi có trễ.

### Nhận xét từng biểu đồ

**Biểu đồ 4 — Tỷ trọng nguyên nhân trễ (Pie chart):** Nguyên nhân do hãng hàng không chiếm tỷ trọng lớn nhất (37,4%), vượt trễ dây chuyền (29,5%) và hệ thống không lưu (24,6%) — khác với xu hướng chung toàn ngành, cho thấy vấn đề vận hành nội bộ của Delta đáng được ưu tiên xem xét.

**Biểu đồ 5 — Tỷ lệ trễ theo giờ khởi hành và ngày trong tuần (Heatmap):** Tỷ lệ trễ tăng dần trong ngày, đạt đỉnh 20,2% lúc 18h (tỷ lệ gộp theo `hour_summary`); Thứ Năm nổi bật với tỷ lệ cao hơn hẳn vào khung chiều-tối trong khi Thứ Bảy thấp nhất. Xu hướng tăng theo giờ được kiểm chứng thêm bằng phân tích trung bình phút trễ dây chuyền theo giờ trong nhóm chuyến đã trễ (tăng từ 1,7-4,6 phút lên 28,7 phút) — đây là số phút trễ trung bình, khác với tỷ lệ trễ.

**Biểu đồ 6 — Phân bố phút trễ theo tháng (Boxplot):** Tháng 5 có median phút trễ cao nhất (40 phút) dù không phải tháng có tần suất trễ cao nhất; tháng 10 thấp nhất cả về tần suất lẫn mức độ nghiêm trọng (30 phút) — xác nhận đây là tháng vận hành tốt nhất trong năm của Delta.

---

## 4. Tổng hợp phát hiện chính

| ID | Khía cạnh | Phát hiện | Giá trị |
|---|---|---|---|
| F1 | Tổng quan | Tỷ lệ trễ chung toàn bộ Delta Air Lines | 13,6% |
| F2 | Mùa vụ | Tháng có tỷ lệ đúng giờ thấp nhất | Tháng 2 — 80,4% |
| F3 | Mùa vụ | Tháng có tỷ lệ đúng giờ cao nhất | Tháng 10 — 92,2% |
| F4 | Sân bay | Sân bay khởi hành có tỷ lệ trễ cao nhất | LGA — 21,1% (cao hơn TB 7,6 điểm %) |
| F5 | Tuyến bay | Tuyến rủi ro cao nhất (≥500 chuyến) | SFO–LAX — 43,8% trên 1.570 chuyến |
| F6 | Nguyên nhân | Nguyên nhân chiếm tỷ trọng lớn nhất | Hãng hàng không — 37,4% |
| F7 | Thời gian | Khung giờ rủi ro cao nhất | 18h — 20,2% |
| F8 | Mức độ nghiêm trọng | Tháng có median phút trễ cao nhất | Tháng 5 — 40 phút |

Số liệu chi tiết của các phát hiện trên được xuất trong tệp `key_findings.csv` đi kèm mã nguồn phân tích.
