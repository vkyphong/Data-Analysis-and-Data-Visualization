# Báo cáo kiểm tra, lọc và làm sạch dữ liệu — Delta Air Lines

## 1. Khai phá sơ bộ dữ liệu gốc `flights.csv`

File `flights.csv` là tập dữ liệu gốc thuộc bộ **2015 Flight Delays and Cancellations** trên Kaggle. Dữ liệu bao gồm thông tin về lịch trình, sân bay, thời gian khởi hành và đến, thời gian trễ, tình trạng hủy chuyến và chuyển hướng của các chuyến bay trong năm 2015.

Qua khảo sát sơ bộ, dữ liệu gốc có các đặc điểm chính:

- **Tổng số dòng:** 5.819.079.
- **Số cột:** 31.
- **Phạm vi thời gian:** từ tháng 1 đến tháng 12 năm 2015.
- **Đối tượng dữ liệu:** các chuyến bay của nhiều hãng hàng không tại Hoa Kỳ.
- **Các nhóm thông tin chính:** mã hãng hàng không, sân bay xuất phát và điểm đến, thời gian dự kiến, thời gian thực tế, độ trễ, hủy chuyến và chuyển hướng.
- **Một số cột có giá trị thiếu**, đặc biệt là các trường liên quan đến thời gian thực tế hoặc thông tin chỉ phát sinh khi chuyến bay bị hủy hay không hoàn thành.

Do mục tiêu nghiên cứu tập trung vào **Delta Air Lines**, dữ liệu được giới hạn theo mã hãng `DL` trước khi thực hiện các bước kiểm tra và làm sạch chi tiết. Cách tiếp cận này giúp phạm vi phân tích phù hợp với đối tượng nghiên cứu và giảm khối lượng dữ liệu cần xử lý.

## 2. Phạm vi nghiên cứu và dữ liệu đầu vào

Bài tập sử dụng bộ dữ liệu **2015 Flight Delays and Cancellations (Kaggle)**. Tuy nhiên, phạm vi phân tích được giới hạn ở hãng **Delta Air Lines**, có mã hãng `DL`.

Các file tham chiếu:
- `flights.zip` (chứa `flights.csv`): dữ liệu chuyến bay gốc.
- `airports.csv`: danh sách mã sân bay IATA hợp lệ.
- `T_MASTER_CORD.csv`: bảng ánh xạ mã `AIRPORT_ID` của BTS sang mã IATA.

## 3. Chiến lược xử lý dữ liệu

Để giảm khối lượng dữ liệu phải xử lý và bảo đảm quy trình phù hợp với mục tiêu nghiên cứu, quy trình xử lý được thực hiện như sau:

```text
flights.csv
    ↓
Lọc AIRLINE == "DL"
    ↓
flights_DL_raw.csv
    ↓
Kiểm tra và làm sạch dữ liệu Delta
    ↓
flights_DL_cleaned.csv
```

Việc lọc được thực hiện ngay sau khi đọc dữ liệu gốc, trước các bước tạo ngày, ánh xạ mã sân bay, xử lý missing values và tạo biến mục tiêu.

## 4. Lọc Delta Air Lines

### 3.1. Cách thực hiện

Điều kiện lọc:

```python
for chunk in pd.read_csv(RAW_PATH, chunksize=500_000, low_memory=False):
    selected = chunk.loc[chunk["AIRLINE"].eq("DL")].copy()
    # Tập hợp các chunk đã lọc thành DataFrame Delta
```

Sau khi lọc, dữ liệu được lưu tạm thành `flights_DL_raw.csv`. File này giữ nguyên trạng thái trước làm sạch, hỗ trợ việc truy vết và so sánh trước–sau xử lý.

### 3.2. Lý do lựa chọn

- Giới hạn dữ liệu theo đúng đối tượng nghiên cứu.
- Giảm số dòng được đưa qua các bước tiền xử lý.
- Giảm nhu cầu sử dụng RAM khi thực hiện các thao tác trên DataFrame.
- Làm cho báo cáo và pipeline nhất quán với mục tiêu phân tích riêng Delta Air Lines.

**Lưu ý:** Số dòng và tỷ lệ dữ liệu sau lọc phải được xác nhận bằng cách chạy notebook trên `flights.csv` thực tế. Không sử dụng số liệu của toàn bộ 13/14 hãng bay để đại diện cho tập Delta.

## 5. Kiểm tra và làm sạch dữ liệu Delta

Sau khi lọc, các bước làm sạch được áp dụng trên DataFrame `df` chỉ chứa các chuyến bay có `AIRLINE == "DL"`.

### 4.1. Tạo ngày bay

Gộp `YEAR`, `MONTH` và `DAY` thành cột `FLIGHT_DATE` kiểu datetime. Cột `DAY_OF_WEEK` được giữ riêng vì đây là biến có thể sử dụng trong phân tích hoặc xây dựng mô hình.

### 4.2. Chuẩn hóa mã sân bay

Các mã sân bay được chuẩn hóa bằng cách:
1. Chuyển về chuỗi, loại bỏ khoảng trắng và viết hoa.
2. Giữ nguyên mã IATA nếu mã đã tồn tại trong `airports.csv`.
3. Tra cứu mã số `AIRPORT_ID` qua `T_MASTER_CORD.csv`.
4. Đánh dấu các mã không xác định bằng cột `..._VALID` và giá trị `UNKNOWN` trong cột `..._CLEAN`.

Kết quả thực tế trên tập Delta:
- Có **75.552 dòng** được ánh xạ từ mã số sang IATA ở `ORIGIN_AIRPORT`.
- Có **75.552 dòng** được ánh xạ từ mã số sang IATA ở `DESTINATION_AIRPORT`.
- Còn **332 mã không tra cứu được** ở `ORIGIN_AIRPORT` và **331 mã không tra cứu được** ở `DESTINATION_AIRPORT`; các giá trị này được đánh dấu là `UNKNOWN`.

### 4.3. Xử lý missing values

- Các cột nguyên nhân trễ được điền `0` cho các chuyến không bị hủy, theo ý nghĩa “không áp dụng”.
- `CANCELLATION_REASON` được điền `"NONE"` khi thiếu.
- `TAIL_NUMBER` được điền `"UNKNOWN"` khi thiếu.
- Các cột hậu chuyến bay như `DEPARTURE_TIME`, `ARRIVAL_TIME`, `TAXI_IN`, `TAXI_OUT` và các cột liên quan được giữ `NaN` khi sự kiện chưa xảy ra.
- `SCHEDULED_TIME` được tính lại từ `SCHEDULED_DEPARTURE` và `SCHEDULED_ARRIVAL` nếu bị thiếu.

Các số liệu missing values trước và sau làm sạch phải được lấy trực tiếp từ tập Delta, không sao chép kết quả thống kê của toàn bộ dữ liệu gốc. Notebook đã tạo thành công file `flights_DL_cleaned.csv`. Các thống kê tổng hợp về giá trị thiếu được trình bày ở phần kết quả kiểm tra sau khi làm sạch.

### 4.4. Tạo biến mục tiêu

Biến `IS_DELAYED` được tạo theo quy tắc:

- `1` nếu `ARRIVAL_DELAY >= 15`.
- `0` nếu chuyến bay có dữ liệu đến và độ trễ dưới 15 phút.
- `NaN` nếu `ARRIVAL_DELAY` bị thiếu, chẳng hạn trong trường hợp chuyến bay bị hủy.

### 4.5. Cảnh báo data leakage

Nếu mục tiêu là dự đoán trễ chuyến trước giờ khởi hành, không sử dụng các biến chỉ xuất hiện sau hoặc trong quá trình chuyến bay diễn ra, chẳng hạn:
`DEPARTURE_TIME`, `DEPARTURE_DELAY`, `TAXI_OUT`, `WHEELS_OFF`, `ELAPSED_TIME`, `AIR_TIME`, `WHEELS_ON`, `TAXI_IN` và `ARRIVAL_TIME`.

## 6. Kết quả tổng hợp

| Hạng mục | Kết quả |
|---|---|
| Tổng số dòng dữ liệu gốc | 5.819.079 |
| Số dòng Delta sau lọc | 875.881 |
| Tỷ lệ Delta trên toàn bộ dữ liệu | ~15,05% |
| Số cột trước làm sạch | 31 |
| Số cột sau làm sạch | 37 |
| Số dòng được ánh xạ ở `ORIGIN_AIRPORT` | 75.552 |
| Số dòng được ánh xạ ở `DESTINATION_AIRPORT` | 75.552 |
| Mã không tra cứu được ở `ORIGIN_AIRPORT` | 332 |
| Mã không tra cứu được ở `DESTINATION_AIRPORT` | 331 |
| File dữ liệu sau làm sạch | `flights_DL_cleaned.csv` |
| Kích thước dữ liệu sau làm sạch | 875.881 dòng × 37 cột |

## 8. Kết quả kiểm tra sau khi làm sạch

Kết quả kiểm tra trực tiếp trên file `flights_DL_cleaned.csv` bằng notebook như sau:

| Hạng mục | Kết quả |
|---|---:|
| Số dòng sau khi làm sạch | 875.881 |
| Số cột sau khi làm sạch | 37 |
| Tổng số giá trị thiếu | 68.331 |
| Số dòng trùng lặp hoàn toàn | 0 |
| Số chuyến bay bị trễ (`IS_DELAYED = 1`) | 118.023 |
| Số chuyến bay không bị trễ (`IS_DELAYED = 0`) | 752.252 |
| Tỷ lệ chuyến bay bị trễ | 13,47% |

Kết quả cho thấy dữ liệu sau làm sạch gồm **875.881 dòng và 37 cột**. Không phát hiện dòng trùng lặp hoàn toàn. Tổng số giá trị thiếu còn lại là **68.331**, trong đó một phần có thể xuất phát từ các trường không áp dụng, chẳng hạn thông tin thời gian thực tế của chuyến bay bị hủy hoặc chưa hoàn thành.

Biến `IS_DELAYED` cho thấy có **118.023 chuyến bay bị trễ**, chiếm **13,47%**, và **752.252 chuyến bay không bị trễ**. Thống kê này được sử dụng để mô tả sự phân bố của biến mục tiêu trong tập dữ liệu Delta sau khi lọc và làm sạch.


## 9. Kết luận

Quy trình xử lý lọc Delta Air Lines trước, sau đó mới kiểm tra và làm sạch dữ liệu. Cách sắp xếp này giúp giảm phạm vi xử lý, tăng tính nhất quán giữa mục tiêu nghiên cứu và dữ liệu sử dụng, đồng thời tạo ra hai mốc dữ liệu rõ ràng: `flights_DL_raw.csv` trước làm sạch và `flights_DL_cleaned.csv` sau làm sạch.

Kết quả chạy notebook xác nhận pipeline đã lọc đúng hãng `DL`, thực hiện ánh xạ mã sân bay và tạo file `flights_DL_cleaned.csv` với kích thước **875.881 dòng × 37 cột**. Sau khi làm sạch, dữ liệu không có dòng trùng lặp hoàn toàn; còn **68.331 giá trị thiếu**. Biến `IS_DELAYED` ghi nhận **118.023 chuyến bay bị trễ**, tương ứng **13,47%**, và **752.252 chuyến bay không bị trễ**. Các kết quả này cung cấp cơ sở cho bước phân tích dữ liệu và trực quan hóa tiếp theo.
