# Phần Machine Learning: Dự đoán chuyến bay trễ (Delta Airlines)

## 1. Bài toán và dữ liệu
Nhóm xây dựng bài toán phân loại (classification) để dự đoán một chuyến bay của Delta Airlines có bị trễ hay không, dựa trên các thông tin đã biết trước khi máy bay cất cánh. Biến mục tiêu là `IS_DELAYED`, quy ước chuyến bay được coi là trễ nếu thời gian đến trễ hơn 15 phút so với lịch (`ARRIVAL_DELAY > 15`).

Dataset gốc từ Kaggle (US DOT Flight Delays) đã được lọc sẵn chỉ còn dữ liệu của Delta, và các chuyến bị hủy/chuyển hướng đã được loại ra trước đó, vì các chuyến này không phản ánh đúng khái niệm "trễ" mà bài toán đang quan tâm.

Một điểm nhóm chú ý ngay từ đầu là **tránh data leakage**: chỉ dùng những feature mà hãng bay biết được ở thời điểm lên lịch bay, chứ không dùng các biến chỉ phát sinh sau khi chuyến bay đã xảy ra (ví dụ thời gian cất/hạ cánh thực tế, các cột breakdown nguyên nhân trễ...). Nếu đưa các biến này vào, model sẽ đạt điểm rất cao nhưng thực chất là "nhìn thấy đáp án", không dùng được để dự đoán cho chuyến bay tương lai.

Các feature được dùng: `MONTH`, `DAY`, `DAY_OF_WEEK`, sân bay đi/đến, `DISTANCE`, giờ khởi hành theo lịch (`scheduled_hour`, `scheduled_minute`), và `ROUTE` (cặp sân bay đi-đến) — feature này được tạo thêm để model nắm được đặc thù riêng của từng tuyến bay cụ thể.

## 2. Cách chia tập Train/Test

Nhóm chia dữ liệu theo thời gian thay vì chia ngẫu nhiên (random split): các tháng đầu năm dùng để train, các tháng cuối năm dùng để test.

Lý do chọn cách này: bài toán thực tế là dự đoán cho các chuyến bay trong tương lai, dựa trên dữ liệu quá khứ. Nếu chia ngẫu nhiên, model có thể được train trên cả dữ liệu tháng 12 rồi đem test trên tháng 6, điều này không đúng với cách model sẽ được dùng khi triển khai thật (lúc đó model chỉ có dữ liệu quá khứ để học, chưa từng thấy tương lai). Chia theo thời gian giúp mô phỏng đúng tình huống vận hành thực tế, đồng thời cũng giúp phát hiện được model có bị lệch theo mùa hay không (ví dụ học tốt ở các tháng ít trễ nhưng dự đoán kém vào mùa cao điểm cuối năm).

## 3. Hai mô hình sử dụng

Nhóm xây dựng và so sánh 2 mô hình:

**Logistic Regression (baseline).** Model này tính một tổ hợp tuyến tính từ các feature đầu vào rồi đưa qua hàm sigmoid để ra xác suất trễ. Đây là lựa chọn baseline vì đơn giản, huấn luyện nhanh, và dễ diễn giải, nếu model phức tạp hơn không tốt hơn được baseline này, đó là tín hiệu cần xem lại dữ liệu/feature chứ không phải cứ dùng model phức tạp là tốt hơn.

**Random Forest (mô hình nâng cao).** Đây là tập hợp của nhiều cây quyết định (decision tree), mỗi cây học trên một tập con ngẫu nhiên của dữ liệu, kết quả cuối là bỏ phiếu/trung bình từ tất cả các cây. Random Forest được chọn vì có thể bắt được các mối quan hệ phi tuyến tính và tương tác giữa các feature, điều mà Logistic Regression khó làm được nếu không tạo thêm biến tương tác thủ công. Ngoài ra, Random Forest cũng cho phép trích xuất feature importance, phục vụ cho phần diễn giải model bên dưới.

## 4. Kết quả và so sánh 2 model

| Model | Accuracy | Precision | Recall | F1 | ROC-AUC |
|---|---|---|---|---|---|
| Logistic Regression | 0.645 | 0.143 | 0.428 | 0.214 | 0.567 |
| Random Forest | 0.598 | 0.143 | 0.508 | 0.223 | 0.576 |

Nhìn thoáng qua thì Logistic Regression có Accuracy cao hơn, nhưng con số này gây hiểu lầm trong bài toán này. Vì tỷ lệ chuyến trễ chỉ chiếm một phần nhỏ trong dữ liệu, một model thiên về dự đoán "không trễ" vẫn có thể đạt Accuracy cao mà không thực sự hữu ích.

Điều nhóm quan tâm hơn là Recall, tỷ lệ trong số các chuyến thực sự bị trễ, model bắt được bao nhiêu phần trăm. Recall thấp nghĩa là bỏ sót nhiều chuyến trễ thật, và trong bối cảnh bài toán này, bỏ sót một chuyến sắp trễ sẽ khiến hãng bay không kịp chuẩn bị máy bay dự phòng hay nhân sự, hậu quả nặng hơn nhiều so với việc cảnh báo dư (False Positive chỉ tốn công chuẩn bị không cần thiết).

Random Forest có Recall cao hơn rõ rệt (0.508 so với 0.428), đồng thời F1 và ROC-AUC cũng nhỉnh hơn. Vì vậy nhóm chọn **Random Forest** làm model chính để xác định chuyến bay có nguy cơ trễ.

Nhìn vào confusion matrix cũng thấy rõ hơn: Logistic Regression bỏ sót 14.102 chuyến trễ thật, trong khi Random Forest chỉ bỏ sót 12.133 chuyến, giảm được khoảng 2.000 ca so với baseline.

Cả 2 model đều có Precision khá thấp (0.143), tức phần lớn các cảnh báo SẼ TRỄ hóa ra là báo động giả. Đây là đánh đổi khi ưu tiên không bỏ sót chuyến trễ thật (dùng `class_weight='balanced'` để xử lý mất cân bằng lớp), nhóm chấp nhận đánh đổi này vì hậu quả của việc bỏ sót nặng hơn.

## 5. Diễn giải mô hình — Feature Importance

Nhóm dùng feature importance của Random Forest để xem yếu tố nào ảnh hưởng nhiều nhất đến khả năng trễ chuyến.

Top 10 feature quan trọng nhất: `scheduled_hour` (0.355), `DAY` (0.098), `MONTH_9` (0.062), sân bay đến LGA (0.056), `MONTH_2` (0.042), `DISTANCE` (0.039), sân bay đi LGA (0.031), thứ 4 trong tuần (0.025), nhóm sân bay đi khác (0.025), `scheduled_minute` (0.024).

Điều nổi bật nhất là `scheduled_hour` chiếm tỷ trọng áp đảo, cao gấp hơn 3,5 lần feature đứng thứ hai. Điều này khớp với một hiện tượng thường gặp trong vận hành hàng không: các chuyến bay càng muộn trong ngày càng dễ bị dồn trễ từ những chuyến trước đó dùng chung máy bay hoặc tổ bay (cascading delay). Khi nhóm phân tích xác suất trễ trung bình theo giờ khởi hành, số liệu cũng cho thấy đúng xu hướng này: xác suất trễ tăng dần từ sáng đến chiều tối, thấp nhất vào sáng sớm (khoảng 0,39–0,44) và đạt đỉnh ở khung 17h–21h (khoảng 0,54–0,55).

Sân bay LGA (LaGuardia) xuất hiện ở cả vai trò sân bay đi và sân bay đến trong top 10, cho thấy đây là điểm nghẽn đáng chú ý trong mạng bay, phù hợp với thực tế LGA vốn nổi tiếng đông đúc và hạn chế về slot đường băng.

## 6. Phân tích tuyến bay có nguy cơ cao

Từ xác suất dự đoán của Random Forest, nhóm tính xác suất trễ trung bình theo từng route để tìm ra các tuyến rủi ro nhất.

| Route | Xác suất trễ TB | Số chuyến |
|---|---|---|
| ATL → LGA | 0.596 | 965 |
| LGA → ATL | 0.556 | 968 |
| ATL → BOS | 0.505 | 641 |
| ATL → LAX | 0.501 | 650 |
| ATL → DCA | 0.496 | 806 |

Hai tuyến rủi ro cao nhất đều liên quan đến LGA (cả 2 chiều), xác suất trễ trung bình gần 60% — cao hơn hẳn mặt bằng chung. Điều này củng cố thêm phát hiện ở phần feature importance. Các tuyến còn lại trong top 10 hầu hết đều xuất phát từ ATL (hub chính của Delta) với xác suất khá đồng đều quanh 0,49–0,50, cho thấy rủi ro trễ không nằm ở một vài tuyến cá biệt mà là đặc điểm chung của các chuyến khởi hành từ hub này.

Khi lọc nhóm chuyến có xác suất trễ rất cao (≥ 0,7), chỉ có 114 chuyến trong tổng số chuyến test (khoảng 0,05%) rơi vào nhóm này. Con số này khá nhỏ, cho thấy model hiếm khi "tự tin cao" về một chuyến sẽ trễ — phần lớn dự đoán nằm ở vùng xác suất trung bình. Vì vậy nhóm cho rằng ngưỡng 0,7 chưa thực sự phù hợp để dùng làm tiêu chí vận hành; nếu áp dụng thực tế, có thể cân nhắc hạ ngưỡng xuống khoảng 0,5–0,55 để nhóm rủi ro cao có quy mô đủ lớn, hữu ích hơn cho việc lên kế hoạch nguồn lực.

## 7. Insight cho ban điều hành

Từ các kết quả trên, nhóm rút ra 3 đề xuất chính:

**Ưu tiên nguồn lực cho khung giờ chiều tối.** Rủi ro trễ tăng rõ rệt từ 17h đến 21h, cao hơn buổi sáng sớm khoảng 10–15 điểm phần trăm. Hãng nên cân nhắc bố trí máy bay/tổ bay dự phòng tập trung vào khung giờ này, đặc biệt với các chuyến nối tiếp nhau trong ngày.

**Chú ý đặc biệt đến tuyến qua LGA.** Cả 2 chiều ATL–LGA đều có xác suất trễ trung bình gần 60%, cao nhất trong toàn bộ mạng bay. Có thể cân nhắc thêm thời gian đệm cho việc quay đầu máy bay ở tuyến này, hoặc phối hợp sát hơn với việc quản lý slot tại LGA.

**Cải thiện vận hành chung ở hub ATL.** Vì phần lớn các tuyến rủi ro cao đều xuất phát từ ATL với mức rủi ro khá đồng đều, vấn đề có vẻ mang tính hệ thống hơn là cá biệt ở một vài tuyến, nên hướng xử lý phù hợp là cải thiện quy trình vận hành chung tại hub, thay vì chỉ tập trung vào từng tuyến riêng lẻ.

## 8. Kết luận và hạn chế

Random Forest cho kết quả cân bằng hơn Logistic Regression ở các chỉ số quan trọng (Recall, F1, ROC-AUC), nên được chọn làm model chính. Tuy nhiên, cần nhìn nhận thẳng thắn rằng hiệu suất tổng thể của cả 2 model còn khá khiêm tốn, ROC-AUC chỉ khoảng 0,57, nhỉnh hơn không đáng kể so với đoán ngẫu nhiên (0,5). Điều này cho thấy các feature hiện có (thời gian, sân bay, khoảng cách) chưa đủ để giải thích phần lớn nguyên nhân gây trễ chuyến bay.

Để cải thiện trong các bước tiếp theo, nhóm đề xuất bổ sung thêm dữ liệu thời tiết, tình trạng không lưu, hoặc lịch sử vận hành của từng máy bay, tổ bay — đây là những yếu tố có khả năng ảnh hưởng lớn đến việc trễ chuyến nhưng chưa được đưa vào mô hình hiện tại do giới hạn của dataset.
