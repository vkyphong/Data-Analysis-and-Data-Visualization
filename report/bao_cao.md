# PHÂN TÍCH MÔ TẢ VÀ CHẨN ĐOÁN
## Đề tài: Cải thiện tỷ lệ đúng giờ của hãng hàng không
Thực hiện: Nguyễn Minh Quân | Nguồn dữ liệu: Kaggle usdot/flight-delays (2015)

---

## Câu hỏi nghiên cứu

*"Những yếu tố nào làm tăng nguy cơ chuyến bay bị trễ, và hãng hàng không nên ưu tiên tuyến bay/thời điểm nào để chủ động bố trí nguồn lực trước mùa cao điểm?"*

Câu hỏi này được trả lời qua 4 lớp phân tích theo trình tự: Mô tả (chuyện gì đang xảy ra), Chẩn đoán (vì sao xảy ra), Dự đoán (chuyến nào có nguy cơ trễ) và Chỉ định (nên làm gì). Phần dưới đây trình bày hai lớp đầu tiên: Mô tả và Chẩn đoán.

---

## 1. Dữ liệu và phạm vi phân tích

Dữ liệu sử dụng gồm `flights_cleaned.csv` và `airlines.csv`, là bản dữ liệu chuyến bay nội địa Hoa Kỳ năm 2015 đã qua bước làm sạch. Biến mục tiêu `IS_DELAYED` được xác định trực tiếp từ `ARRIVAL_DELAY`: bằng 1 nếu trễ từ 15 phút trở lên (theo chuẩn của Bộ Giao thông Hoa Kỳ - US DOT), bằng 0 nếu đúng giờ, và không xác định nếu chuyến bay không có giá trị `ARRIVAL_DELAY` (chủ yếu là các chuyến bị hủy).

Toàn bộ phân tích chỉ xét các chuyến bay không bị chuyển hướng (`DIVERTED = 0`), nhằm đảm bảo `ARRIVAL_DELAY` phản ánh đúng thời gian đến sân bay đích ban đầu. Trong 5.819.079 chuyến ban đầu, có 15.187 chuyến bị chuyển hướng và được loại khỏi phân tích, còn lại 5.803.892 chuyến. Trong số này, 5.714.008 chuyến hoàn thành và có đầy đủ thông tin để tính tỷ lệ trễ; phần chênh lệch là các chuyến bị hủy.

---

## 2. Phân tích Mô tả (Descriptive Analysis)

*Trình tự trình bày: Tổng quan → Hãng nào? → Tuyến nào?*

Trên tập dữ liệu đủ điều kiện phân tích (5.714.008 chuyến), tỷ lệ chuyến bay bị trễ từ 15 phút trở lên là 18,6%, tức trung bình cứ khoảng 5-6 chuyến bay thì có 1 chuyến trễ. Tỷ lệ đúng giờ không ổn định quanh năm mà dao động rõ rệt theo mùa: thấp nhất vào tháng 6 (76,5% đúng giờ) và cao nhất vào tháng 10 (87,6% đúng giờ), chênh lệch 11,1 điểm phần trăm. Điều này phù hợp với đặc điểm mùa cao điểm du lịch hè gây áp lực lớn lên lịch bay và hạ tầng sân bay.

Xét theo hãng bay, mức độ trễ chênh lệch rất lớn: Spirit Air Lines có tỷ lệ trễ cao nhất (29,7%), cao hơn trung bình toàn ngành 11,1 điểm phần trăm, trong khi Hawaiian Airlines có tỷ lệ trễ thấp nhất (11,3%). Ở cấp độ tuyến bay, sau khi loại 485.332 chuyến có mã sân bay không hợp lệ (8,36% dữ liệu) và loại tiếp các chuyến bị hủy trước khi tính số chuyến mỗi tuyến (để đảm bảo mẫu số dùng cho ngưỡng thống kê khớp với mẫu số dùng tính tỷ lệ trễ), từ 4.656 tuyến thật, có 2.831 tuyến đạt ngưỡng tối thiểu 500 chuyến. Trong nhóm này, tuyến ORD–ASE (Chicago O'Hare – Aspen) có tỷ lệ trễ cao nhất: 40,6% trên 569 chuyến, theo sát là DFW–HNL (Dallas/Fort Worth – Honolulu, cũng 40,6% trên 688 chuyến). Đáng chú ý, khoảng một nửa trong top 10 tuyến rủi ro cao nhất (ORD–ASE/Aspen, DFW–HNL/Honolulu, LGA–MYR/Myrtle Beach, MIA–STT/St Thomas) là các tuyến bay đến điểm đến nghỉ dưỡng — gợi ý nguyên nhân có thể liên quan đến tần suất khai thác thấp hoặc đặc thù thời tiết khu vực (núi, đảo). Những khác biệt lớn theo hãng và theo tuyến cho thấy nguy cơ trễ chuyến không phân bố đều, mà tập trung vào một số hãng và tuyến cụ thể.

### Nhận xét từng biểu đồ

**Biểu đồ 1 — Tỷ lệ đúng giờ theo tháng (Line chart):** Tỷ lệ đúng giờ dao động mạnh theo mùa, thấp nhất tháng 6 (76,5%) và cao nhất tháng 10 (87,6%), chênh lệch 11,1 điểm %, cho thấy mùa cao điểm hè gây áp lực rõ rệt lên lịch bay.

**Biểu đồ 2 — Tỷ lệ trễ theo hãng (Bar chart):** Spirit Air Lines có tỷ lệ trễ cao nhất (29,7%), vượt trung bình ngành 11,1 điểm %, trong khi Hawaiian Airlines thấp nhất (11,3%), cho thấy mức độ trễ phụ thuộc rõ rệt vào năng lực vận hành từng hãng.

**Biểu đồ 3 — Route Risk: khối lượng khai thác so với tỷ lệ trễ (Scatter chart):** Trong nhóm 2.831 tuyến đạt ngưỡng thống kê (sau khi loại chuyến có mã sân bay không hợp lệ và chuyến bị hủy khỏi mẫu số), ORD–ASE có tỷ lệ trễ cao nhất (40,6% trên 569 chuyến), gần như ngang bằng DFW–HNL (40,6% trên 688 chuyến). Các điểm thuộc top 10 rủi ro cao nhất đa phần nằm phía trên đường trung bình ngành và có khối lượng khai thác thấp hơn nhóm tuyến lớn. Cách trình bày dạng scatter cho phép quan sát đồng thời quy mô khai thác và mức độ rủi ro, tránh nhầm lẫn giữa "tuyến đông khách nhất" và "tuyến rủi ro nhất".

---

## 3. Phân tích Chẩn đoán (Diagnostic Analysis)

*Trình tự trình bày: Nguyên nhân gì? → Khi nào? → Nghiêm trọng thế nào?*

Phân tích 5 nhóm nguyên nhân trễ được ghi nhận trong dữ liệu cho thấy nhóm chiếm tỷ trọng phút trễ lớn nhất không phải yếu tố khách quan như thời tiết hay an ninh, mà là trễ dây chuyền do máy bay đến trễ từ chuyến bay trước (39,8% tổng số phút trễ), tiếp theo là nguyên nhân được ghi nhận trực tiếp cho hãng bay (32,2%) và hệ thống không lưu quốc gia (22,9%). Thời tiết chỉ chiếm 4,9% và an ninh gần như không đáng kể (0,1%). Kết quả này gợi ý hãng hàng không nên ưu tiên xem xét lịch quay vòng máy bay và độ trễ tích lũy giữa các chuyến, dù đây là một giả thuyết vận hành hợp lý dựa trên phân loại nguyên nhân của dữ liệu, chưa phải kết luận nhân quả được kiểm chứng độc lập.

Phân tích theo khung giờ và ngày trong tuần cho thấy tỷ lệ trễ thấp nhất vào sáng sớm (5h-9h) và tăng dần trong ngày, đạt đỉnh vào khung 18h-20h (tỷ lệ trễ trung bình cao nhất là 26,1% lúc 20h) ở hầu hết các ngày. Để kiểm chứng thay vì chỉ suy diễn từ pattern này, nhóm tính thêm trung bình phút `LATE_AIRCRAFT_DELAY` theo từng giờ khởi hành: kết quả cho thấy con số này tăng gần như đơn điệu trong khung giờ hoạt động chính (5h-21h), từ 2,7 phút lúc 5h lên đỉnh 29,9 phút lúc 18h, rồi giảm dần về cuối ngày. Xu hướng tăng dần và rõ ràng này phù hợp với giả thuyết trễ dây chuyền — máy bay bay nhiều chuyến/ngày, các chuyến buổi tối có xu hướng gánh độ trễ tích lũy nhiều hơn — dù đây vẫn là quan hệ tương quan quan sát được, chưa kiểm soát các yếu tố gây nhiễu khác (mùa, thời tiết theo giờ, loại máy bay), nên không khẳng định là quan hệ nhân quả tuyệt đối.

Riêng khung giờ 0h-4h có số liệu trễ dây chuyền dao động bất thường (16-51 phút, không theo xu hướng tăng dần liên tục như các giờ khác). Đây không phải do cỡ mẫu nhỏ (toàn bộ ô trong ma trận giờ×ngày đều có từ 50 chuyến quan sát trở lên), mà nhiều khả năng do đặc thù của số ít chuyến bay khai thác vào khung giờ khuya/rạng sáng. Khung giờ này không được đưa vào lập luận chính về trễ dây chuyền.

Xét mức độ nghiêm trọng khi đã trễ, không chỉ tần suất, Hawaiian Airlines có thời gian trễ trung vị thấp nhất (25 phút) và độ phân tán hẹp nhất — nhất quán với việc hãng này cũng có tỷ lệ trễ thấp nhất ở phần Mô tả, cho thấy đây là hãng có kết quả vận hành ổn định nhất trong phạm vi dữ liệu năm 2015 được phân tích (không suy rộng cho các năm khác hoặc toàn bộ năng lực vận hành của hãng). Ngược lại, Spirit Air Lines không chỉ trễ nhiều nhất mà còn có thời gian trễ trung vị cao nhất (42 phút) với độ phân tán rất rộng, cho thấy đây là hãng có rủi ro vận hành cao nhất trong cùng phạm vi dữ liệu.

### Nhận xét từng biểu đồ

**Biểu đồ 4 — Tỷ trọng nguyên nhân trễ (Pie chart):** Trễ dây chuyền do máy bay đến trễ chuyến trước chiếm tỷ trọng lớn nhất (39,8%), vượt xa nguyên nhân do hãng bay (32,2%) và hệ thống không lưu (22,9%), cho thấy các nguyên nhân liên quan đến vận hành và trễ dây chuyền chiếm tỷ trọng lớn hơn là yếu tố khách quan.

**Biểu đồ 5 — Tỷ lệ trễ theo giờ khởi hành và ngày trong tuần (Heatmap):** Tỷ lệ trễ tăng dần trong ngày, đạt đỉnh 26,1% lúc 20h (tính bằng trung bình tỷ lệ trễ của 7 ngày trong tuần tại khung giờ đó). Số lượng chuyến bay quan sát được ở mỗi ô giờ×ngày được xuất trong tệp `heatmap_hour_dow_count.csv` để kiểm chứng độ tin cậy — toàn bộ 168 ô đều có từ 50 chuyến trở lên. Kết quả xu hướng tăng theo giờ được kiểm chứng thêm bằng phân tích trung bình phút trễ dây chuyền theo giờ (tăng từ 2,7 phút lúc 5h lên 29,9 phút lúc 18h) thay vì chỉ suy diễn từ hình dạng heatmap.

**Biểu đồ 6 — Phân bố phút trễ theo hãng (Boxplot):** Hawaiian Airlines có thời gian trễ trung vị thấp nhất (25 phút), trong khi Spirit Air Lines cao nhất (42 phút), xác nhận hãng trễ nhiều nhất (Biểu đồ 2) cũng là hãng trễ lâu nhất, không chỉ về tần suất mà cả mức độ nghiêm trọng.

---

## 4. Tổng hợp phát hiện chính

| ID | Khía cạnh | Phát hiện | Giá trị |
|---|---|---|---|
| F1 | Tổng quan | Tỷ lệ trễ chung trên tập phân tích | 18,6% |
| F2 | Mùa vụ | Tháng có tỷ lệ đúng giờ thấp nhất | Tháng 6 — 76,5% |
| F3 | Mùa vụ | Tháng có tỷ lệ đúng giờ cao nhất | Tháng 10 — 87,6% |
| F4 | Hãng bay | Hãng có tỷ lệ trễ cao nhất | Spirit Air Lines — 29,7% (cao hơn TB 11,1 điểm %) |
| F5 | Hãng bay | Hãng vận hành ổn định nhất | Hawaiian Airlines — 11,3% |
| F6 | Tuyến bay | Tuyến rủi ro cao nhất (≥500 chuyến) | ORD–ASE — 40,6% trên 569 chuyến |
| F7 | Nguyên nhân | Nguyên nhân chiếm tỷ trọng lớn nhất | Trễ dây chuyền — 39,8% |
| F8 | Thời gian | Khung giờ rủi ro cao nhất | 20h — 26,1% |

Số liệu chi tiết của các phát hiện trên được xuất trong tệp `key_findings.csv` đi kèm mã nguồn phân tích.