# Phần Machine Learning: Dự đoán chuyến bay trễ (Delta Airlines)

## 1. Bài toán và dữ liệu

Nhóm xây dựng bài toán phân loại (classification) để dự đoán một chuyến bay của Delta Airlines có bị trễ hay không, dựa trên các thông tin đã biết trước khi máy bay cất cánh. Biến mục tiêu là `IS_DELAYED`, quy ước chuyến bay được coi là trễ nếu thời gian đến trễ hơn 15 phút so với lịch (`ARRIVAL_DELAY > 15`).

Dataset gốc từ Kaggle (US DOT Flight Delays) đã được lọc sẵn chỉ còn dữ liệu của Delta, và các chuyến bị hủy/chuyển hướng đã được loại ra trước đó, vì các chuyến này không phản ánh đúng khái niệm "trễ" mà bài toán đang quan tâm.

Một điểm nhóm chú ý ngay từ đầu là **tránh data leakage**: chỉ dùng những feature mà hãng bay biết được ở thời điểm lên lịch bay, chứ không dùng các biến chỉ phát sinh sau khi chuyến bay đã xảy ra (ví dụ thời gian cất/hạ cánh thực tế, các cột breakdown nguyên nhân trễ...). Nếu đưa các biến này vào, model sẽ đạt điểm rất cao nhưng thực chất là "nhìn thấy đáp án", không dùng được để dự đoán cho chuyến bay tương lai.

Các feature được dùng:

- `MONTH`
- `DAY`
- `DAY_OF_WEEK`
- Sân bay đi/đến
- `DISTANCE`
- Giờ khởi hành theo lịch (`scheduled_hour`, `scheduled_minute`)
- `ROUTE` (cặp sân bay đi-đến)

Feature `ROUTE` được tạo thêm để model nắm được đặc thù riêng của từng tuyến bay cụ thể.

## 2. Cách chia tập Train/Test

Nhóm chia dữ liệu theo thời gian thay vì chia ngẫu nhiên (random split): 9 tháng đầu năm dùng để train và 3 tháng cuối năm dùng để test.

- Tập train: 652.391 chuyến
- Tập test: 217.884 chuyến
- Tỷ lệ chuyến trễ trong train: 0,143
- Tỷ lệ chuyến trễ trong test: 0,113

Lý do chọn cách này: bài toán thực tế là dự đoán cho các chuyến bay trong tương lai, dựa trên dữ liệu quá khứ.

Nếu chia ngẫu nhiên, model có thể được train trên cả dữ liệu tháng 12 rồi đem test trên tháng 6, điều này không đúng với cách model sẽ được dùng khi triển khai thật, vì lúc đó model chỉ có dữ liệu quá khứ để học và chưa từng thấy tương lai.

Chia theo thời gian giúp mô phỏng đúng tình huống vận hành thực tế, đồng thời cũng giúp phát hiện được model có bị lệch theo mùa hay không.

## 3. Hai mô hình sử dụng

Nhóm xây dựng và so sánh 2 mô hình:

### 3.1. Logistic Regression

Logistic Regression được sử dụng làm baseline.

Model tính một tổ hợp tuyến tính từ các feature đầu vào rồi đưa qua hàm sigmoid để ra xác suất chuyến bay bị trễ.

Đây là lựa chọn baseline vì:

- Cấu trúc tương đối đơn giản.
- Huấn luyện nhanh.
- Dễ diễn giải.
- Có thể dùng làm mốc để đánh giá model phức tạp hơn.

Nếu một model phức tạp hơn không cải thiện được kết quả so với baseline, đó có thể là dấu hiệu cần xem lại dữ liệu hoặc feature thay vì chỉ sử dụng một model phức tạp hơn.

### 3.2. Random Forest

Random Forest được sử dụng làm mô hình nâng cao.

Random Forest là tập hợp của nhiều cây quyết định (Decision Tree). Mỗi cây học trên một tập con ngẫu nhiên của dữ liệu, sau đó kết quả cuối cùng được tổng hợp từ các cây.

Random Forest được lựa chọn vì:

- Có khả năng mô hình hóa các mối quan hệ phi tuyến tính.
- Có thể phát hiện tương tác giữa các feature.
- Không cần tạo thủ công quá nhiều biến tương tác.
- Có thể trích xuất feature importance để phục vụ việc diễn giải mô hình.

## 4. Kết quả và so sánh 2 model

| Model | Accuracy | Precision | Recall | F1 | ROC-AUC |
|---|---:|---:|---:|---:|---:|
| Logistic Regression | 0.631 | 0.142 | 0.449 | 0.216 | 0.570 |
| Random Forest | 0.580 | 0.140 | 0.526 | 0.221 | 0.564 |

Nhìn thoáng qua thì Logistic Regression có Accuracy cao hơn, nhưng con số này có thể gây hiểu lầm trong bài toán này. Vì tỷ lệ chuyến trễ chỉ chiếm một phần nhỏ trong dữ liệu, một model thiên về dự đoán "không trễ" vẫn có thể đạt Accuracy tương đối cao mà không thực sự hữu ích trong việc phát hiện các chuyến trễ.

Điều nhóm quan tâm hơn là Recall, tức tỷ lệ trong số các chuyến thực sự bị trễ mà model phát hiện được.

Recall thấp nghĩa là model bỏ sót nhiều chuyến trễ thật. Trong bối cảnh bài toán này, việc bỏ sót một chuyến sắp trễ có thể khiến hãng bay không kịp chuẩn bị nguồn lực cần thiết, trong khi cảnh báo dư có thể chỉ làm phát sinh thêm chi phí hoặc công sức chuẩn bị.

Random Forest có Recall cao hơn:

- Random Forest: 0.526
- Logistic Regression: 0.449

F1 của Random Forest cũng cao hơn nhẹ:

- Random Forest: 0.221
- Logistic Regression: 0.216

Tuy nhiên, Logistic Regression có Accuracy và ROC-AUC cao hơn:

- Accuracy: 0.631 so với 0.580
- ROC-AUC: 0.570 so với 0.564

Vì mục tiêu vận hành của nhóm là ưu tiên phát hiện được nhiều chuyến trễ, Random Forest được sử dụng làm model chính dựa trên Recall và F1. Tuy nhiên, cần lưu ý rằng khả năng phân biệt tổng thể của Random Forest chưa vượt baseline Logistic Regression.

### 4.1. Phân tích Confusion Matrix

Nhìn vào confusion matrix:

- Logistic Regression bỏ sót 13.598 chuyến trễ thật.
- Random Forest bỏ sót 11.685 chuyến trễ thật.
- Random Forest giảm được 1.913 trường hợp bỏ sót so với Logistic Regression.

Đổi lại, Random Forest tạo ra nhiều cảnh báo dương tính giả hơn:

- Logistic Regression: 66.762 False Positive.
- Random Forest: 79.727 False Positive.

Cả 2 model đều có Precision khá thấp:
- Logistic Regression: 0.142
- Random Forest: 0.140

Điều này cho thấy khi model cố gắng phát hiện nhiều chuyến trễ hơn, số lượng cảnh báo nhầm cũng tăng lên.

Nhóm sử dụng `class_weight='balanced'` để xử lý tình trạng mất cân bằng giữa hai lớp.

## 5. Diễn giải mô hình — Feature Importance

Nhóm sử dụng feature importance của Random Forest để xem những feature nào đóng góp nhiều nhất vào mô hình.

### Top 10 feature quan trọng nhất

| Feature | Importance |
|---|---:|
| `scheduled_hour` | 0.359 |
| `DAY` | 0.094 |
| `MONTH_9` | 0.060 |
| Sân bay đến LGA | 0.053 |
| `MONTH_2` | 0.045 |
| `DISTANCE` | 0.038 |
| Sân bay đi LGA | 0.034 |
| Nhóm sân bay đi khác | 0.025 |
| Thứ 4 trong tuần | 0.023 |
| `scheduled_minute` | 0.023 |

Điều nổi bật nhất là `scheduled_hour` chiếm tỷ trọng áp đảo, cao gần 3,8 lần feature đứng thứ hai là `DAY`.

Khi nhóm phân tích xác suất trễ trung bình theo giờ khởi hành, số liệu cho thấy xu hướng tăng rõ từ chiều:

- Mức thấp nhất: khoảng 0,396 tại 5h.
- Mức cao nhất: khoảng 0,559 tại 18h.
- Giai đoạn 17h–21h: khoảng 0,551–0,559.

Điều này cho thấy các chuyến bay khởi hành càng muộn trong ngày có xu hướng có xác suất trễ dự đoán cao hơn. Một khả năng có thể giải thích hiện tượng này là trễ dây chuyền (cascading delay), khi một chuyến bay bị trễ làm ảnh hưởng đến các chuyến tiếp theo sử dụng cùng máy bay hoặc tổ bay.

Sân bay LGA xuất hiện ở cả vai trò sân bay đi và sân bay đến trong top 10 feature quan trọng. Đây là một dấu hiệu đáng chú ý cho thấy các chuyến bay liên quan đến LGA có mức rủi ro cao hơn trong mô hình.

## 6. Phân tích dự đoán

### 6.1. Mục tiêu

Mục tiêu của phần phân tích dự đoán là sử dụng Random Forest để ước lượng xác suất một chuyến bay có nguy cơ bị trễ.
Model không nên được hiểu là công cụ khẳng định chắc chắn chuyến bay sẽ trễ. Kết quả phù hợp hơn với việc:
- Xếp hạng mức độ rủi ro.
- Sàng lọc các chuyến cần chú ý.
- Hỗ trợ bộ phận vận hành ưu tiên nguồn lực.

Do Precision của model còn thấp, việc sử dụng dự đoán cũng cần chấp nhận một lượng cảnh báo nhầm.

### 6.2. Phân tích tuyến bay có nguy cơ cao

Từ xác suất dự đoán của Random Forest, nhóm tính xác suất trễ trung bình theo từng route.

| Route | Xác suất trễ TB | Số chuyến |
|---|---:|---:|
| ATL → LGA | 0.591 | 1.455 |
| LGA → ATL | 0.553 | 1.460 |
| ATL → BOS | 0.502 | 981 |
| ATL → LAX | 0.495 | 979 |
| ATL → DCA | 0.491 | 1.235 |

Hai tuyến có xác suất trễ trung bình cao nhất đều liên quan đến LGA:

- ATL → LGA: 0.591
- LGA → ATL: 0.553

Cả hai đều có xác suất trễ trung bình gần 60%.

Các tuyến còn lại trong nhóm có xác suất khoảng 0,49–0,50 và phần lớn xuất phát từ ATL. Điều này cho thấy rủi ro trễ có thể liên quan đến hoạt động tại hub ATL chứ không chỉ tập trung ở một vài tuyến riêng lẻ.

### 6.3. Phân tích nhóm có xác suất rủi ro cao

Khi lọc nhóm chuyến có xác suất trễ dự đoán từ 0,7 trở lên, có:

- 189 chuyến.
- Tổng số chuyến test: 217.884 chuyến.
- Tỷ lệ: 0,09%.

Như vậy, model hiếm khi đưa ra xác suất rất cao. Phần lớn các dự đoán nằm trong vùng xác suất trung bình.

Điều này cho thấy ngưỡng 0,7 tạo ra một nhóm cảnh báo rất nhỏ. Việc lựa chọn ngưỡng cảnh báo vận hành cần được đánh giá thêm dựa trên khả năng cung cấp nguồn lực và chi phí của cảnh báo nhầm.

### 6.4. Kết luận phân tích dự đoán

Từ kết quả của model, rủi ro dự đoán tập trung ở một số nhóm chính:

- Các chuyến khởi hành vào cuối ngày, đặc biệt trong khoảng 17h–21h.
- Các chuyến liên quan đến LGA, nổi bật là ATL–LGA và LGA–ATL.
- Các tuyến có tỷ lệ trễ quan sát cao trong phân tích mô tả, chẳng hạn SFO–LAX và LAX–SFO.

Tuy nhiên, kết quả dự đoán chỉ nên được sử dụng để hỗ trợ sàng lọc và ưu tiên nguồn lực, không nên xem là bằng chứng chắc chắn về nguyên nhân hoặc kết quả của một chuyến bay cụ thể.

## 7. Phân tích đề xuất

Phần này chuyển các kết quả từ phân tích mô tả, chẩn đoán và dự đoán thành những hướng hành động có thể kiểm chứng.

### 7.1. Ưu tiên nguồn lực cho khung giờ chiều tối

Kết quả feature importance cho thấy `scheduled_hour` là feature quan trọng nhất với importance 0.359.

Ngoài ra, xác suất trễ dự đoán trong khoảng 17h–21h dao động khoảng 0,551–0,559, cao hơn rõ rệt so với mức khoảng 0,396 ở 5h.

Do đó, hãng có thể cân nhắc:

- Bố trí nhân sự điều phối dự phòng trong khung giờ 17h–21h.
- Chuẩn bị nguồn lực hỗ trợ cho các chuyến nối tiếp nhau trong ngày.
- Ưu tiên các chuyến có xác suất rủi ro cao thay vì áp dụng cùng một mức chuẩn bị cho toàn bộ lịch bay.

Không nên áp dụng buffer cho toàn bộ chuyến bay vì Precision của mô hình còn thấp.

### 7.2. Rà soát vận hành tại LGA và ATL

Hai tuyến ATL–LGA và LGA–ATL có xác suất trễ trung bình lần lượt là 0.591 và 0.553.

Do đó, nhóm đề xuất rà soát:

- Thời gian quay đầu máy bay.
- Phân bổ gate.
- Lịch nối chuyến.
- Ảnh hưởng của chuyến bay đến trước.
- Các yếu tố vận hành tại LGA.

Ngoài ra, nhiều tuyến rủi ro cao có điểm xuất phát từ ATL. Vì vậy, cần xem xét cả hoạt động ở cấp hub ATL thay vì chỉ xử lý từng route riêng lẻ.

### 7.3. Điều tra riêng SFO–LAX và LAX–SFO

Trong phân tích mô tả, hai tuyến:

- SFO → LAX có tỷ lệ trễ 43,8% trên 1.570 chuyến.
- LAX → SFO có tỷ lệ trễ 35,4% trên 1.569 chuyến.

Đây là cơ sở để nhóm tiếp tục phân tích nguyên nhân của hai tuyến này.

Tuy nhiên, các số liệu trên chưa đủ để kết luận rằng cần cắt hoặc thay đổi lịch bay. Trước khi đưa ra quyết định, cần kiểm tra thêm các yếu tố như thời tiết, không lưu và lịch khai thác.

### 7.4. Lập kế hoạch theo mùa

Phân tích dữ liệu cho thấy:

- Tháng 2 có tỷ lệ đúng giờ thấp nhất, ở mức 80,4%.
- Tháng 5 có median thời gian trễ cao nhất, ở mức 40 phút.

Hai kết quả này phản ánh hai loại vấn đề khác nhau.

Đối với tháng 2, hãng cần chuẩn bị năng lực xử lý số lượng chuyến trễ nhiều hơn.

Đối với tháng 5, do thời gian trễ trung vị cao, cần chú ý đến các phương án phục hồi khi xảy ra sự cố kéo dài.

### 7.5. Đánh giá hiệu quả

Các biện pháp đề xuất cần được thử nghiệm và đánh giá bằng dữ liệu thay vì áp dụng ngay trên toàn bộ mạng bay.
Có thể sử dụng phương pháp so sánh trước–sau hoặc nhóm đối chứng.
Các chỉ số cần theo dõi gồm:

- Tỷ lệ chuyến trễ từ 15 phút.
- Median số phút trễ.
- Số chuyến bị trễ dây chuyền.
- Tỷ lệ hủy/chuyển hướng.
- Recall và Precision của hệ thống cảnh báo.
- Tỷ lệ cảnh báo được xử lý thành công.
- Chi phí nguồn lực bổ sung.

Nếu thử nghiệm cho thấy tác động tích cực, các biện pháp mới có thể được mở rộng.
Đồng thời, nhóm đề xuất bổ sung thêm dữ liệu thời tiết, tình trạng không lưu và lịch sử vận hành của máy bay/tổ bay để cải thiện khả năng dự đoán.

## 8. Kết luận và hạn chế
### 8.1. Kết luận
Nhóm xây dựng bài toán classification để dự đoán chuyến bay của Delta Airlines có bị trễ hay không, sử dụng các thông tin có thể biết trước thời điểm máy bay cất cánh.
Hai mô hình được xây dựng gồm Logistic Regression và Random Forest.
Random Forest đạt Recall 0.526 và F1 0.221, cao hơn Logistic Regression lần lượt là 0.449 và 0.216.
Trong khi đó, Logistic Regression có Accuracy 0.631 và ROC-AUC 0.570, cao hơn Random Forest với Accuracy 0.580 và ROC-AUC 0.564.
Với mục tiêu ưu tiên phát hiện được nhiều chuyến có nguy cơ trễ, nhóm sử dụng Random Forest làm model chính. Tuy nhiên, kết quả cũng cho thấy khả năng phân biệt của cả hai model còn hạn chế, với ROC-AUC chỉ khoảng 0,56–0,57.
Feature importance cho thấy `scheduled_hour` là yếu tố nổi bật nhất, với importance 0.359. Các chuyến khởi hành vào khoảng 17h–21h có xác suất trễ dự đoán cao hơn.
Ngoài ra, các tuyến liên quan đến LGA, đặc biệt ATL–LGA và LGA–ATL, cũng có xác suất trễ dự đoán cao.
### 8.2. Hạn chế
Mô hình hiện tại còn một số hạn chế:
- ROC-AUC chỉ khoảng 0,56–0,57.
- Precision của cả hai model đều thấp.
- Các feature hiện tại chủ yếu gồm thời gian, sân bay và khoảng cách.
- Chưa có dữ liệu thời tiết.
- Chưa có dữ liệu tình trạng không lưu.
- Chưa có lịch sử vận hành của máy bay.
- Chưa có thông tin về tổ bay.
- Chưa thể giải thích đầy đủ nguyên nhân gây ra delay.

Do đó, kết quả hiện tại phù hợp hơn với mục đích sàng lọc và xếp hạng rủi ro thay vì dự đoán chắc chắn chuyến bay nào sẽ bị trễ.
