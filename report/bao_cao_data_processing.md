# Báo cáo kiểm tra và làm sạch dữ liệu — `flights.csv`

**Bộ dữ liệu:** 2015 Flight Delays and Cancellations (Kaggle)
**File xử lý chính:** `flights.csv` (kèm 2 bảng tham chiếu: `airports.csv`, `T_MASTER_CORD.csv` từ BTS)

---

## 1. Kiểm tra dữ liệu đầu vào

Trước khi làm sạch, dữ liệu được khảo sát tổng quan để nắm được quy mô, kiểu dữ liệu và các vấn đề tiềm ẩn.

### 1.1. Quy mô dữ liệu

| Mục | Giá trị |
|---|---|
| Số dòng | 5.819.079 |
| Số cột | 31 |
| Dung lượng file | ~565 MB |
| Đơn vị thời gian | Năm 2015, đầy đủ 12 tháng |

### 1.2. Cấu trúc cột

31 cột gốc chia thành các nhóm:

- **Thông tin chuyến bay:** `YEAR`, `MONTH`, `DAY`, `DAY_OF_WEEK`, `AIRLINE`, `FLIGHT_NUMBER`, `TAIL_NUMBER`
- **Sân bay:** `ORIGIN_AIRPORT`, `DESTINATION_AIRPORT`
- **Giờ theo lịch trình:** `SCHEDULED_DEPARTURE`, `SCHEDULED_ARRIVAL`, `SCHEDULED_TIME`
- **Giờ thực tế:** `DEPARTURE_TIME`, `ARRIVAL_TIME`, `TAXI_OUT`, `TAXI_IN`, `WHEELS_OFF`, `WHEELS_ON`, `ELAPSED_TIME`, `AIR_TIME`
- **Độ trễ:** `DEPARTURE_DELAY`, `ARRIVAL_DELAY`, và 5 cột chi tiết theo nguyên nhân (`AIR_SYSTEM_DELAY`, `SECURITY_DELAY`, `AIRLINE_DELAY`, `LATE_AIRCRAFT_DELAY`, `WEATHER_DELAY`)
- **Trạng thái chuyến bay:** `CANCELLED`, `DIVERTED`, `CANCELLATION_REASON`, `DISTANCE`

### 1.3. Kiểm tra chất lượng ban đầu

| Kiểm tra | Kết quả |
|---|---|
| Dòng trùng lặp hoàn toàn | 0 |
| Giá trị `DEPARTURE_DELAY` / `ARRIVAL_DELAY` âm | Có (từ -87 đến -82 phút) |
| Số chuyến bị hủy (`CANCELLED = 1`) | 89.884 |
| Số chuyến bị chuyển hướng (`DIVERTED = 1`) | 15.187 |
| Mã sân bay không khớp `airports.csv` | 486.165 dòng (cả `ORIGIN` lẫn `DESTINATION`) |

---

## 2. Những gì phát hiện được khi đọc dữ liệu

Từ bước khảo sát trên, 3 đặc điểm quan trọng của dữ liệu được xác định — đây là cơ sở quyết định toàn bộ cách làm sạch ở Mục 3:

### 2.1. Giá trị thiếu (`NaN`) phần lớn là **có chủ đích**, không phải lỗi

Khi thống kê tỷ lệ thiếu theo cột, các cột thiếu nhiều nhất (81–98%) đều là:

- 5 cột lý do trễ (`AIR_SYSTEM_DELAY`...) — thiếu **81,7%**
- `CANCELLATION_REASON` — thiếu **98,46%**

Đối chiếu với số chuyến bị hủy/trễ dưới 15 phút cho thấy các giá trị thiếu này trùng khớp gần như tuyệt đối: chúng thiếu **vì không áp dụng** (chuyến không hủy thì không có lý do hủy; chuyến trễ dưới 15 phút thì không cần chi tiết theo nguyên nhân), không phải vì lỗi thu thập dữ liệu.

Tương tự, các cột "hậu chuyến bay" (`DEPARTURE_TIME`, `ARRIVAL_TIME`, `TAXI_IN/OUT`, `AIR_TIME`...) thiếu ở đúng những chuyến bị hủy hoặc chuyển hướng — vì sự kiện đó **chưa từng xảy ra**, không phải dữ liệu bị mất.

### 2.2. Lỗi hệ thống: mã sân bay tháng 10/2015 sai định dạng

Đối chiếu `ORIGIN_AIRPORT` / `DESTINATION_AIRPORT` với danh sách IATA hợp lệ trong `airports.csv`, phát hiện 486.165 dòng dùng mã số 5 chữ số (ví dụ `14771`) thay vì mã IATA 3 ký tự (ví dụ `SFO`). Phân tích sâu hơn theo tháng và theo hãng bay cho thấy:

- **100% số dòng lỗi này nằm trọn trong tháng 10/2015** (không xuất hiện ở tháng khác)
- Ảnh hưởng đồng thời cả `ORIGIN` và `DESTINATION` trên cùng một dòng (không bao giờ chỉ lỗi một phía)
- Xuất hiện trên 13/14 hãng bay — tức là lỗi ở tầng nguồn dữ liệu, không phải lỗi của riêng một hãng

→ Đây là lỗi hệ thống đã biết của bộ dữ liệu gốc: dữ liệu tháng 10 được trích xuất bằng schema khác (dùng mã DOT Airport ID của Bộ Giao thông Vận tải Mỹ thay vì mã IATA).

### 2.3. Một số ít giá trị thiếu thật sự (lỗi nguồn, không có quy luật)

Riêng cột `SCHEDULED_TIME` (thời lượng bay dự kiến) có 6 dòng bị thiếu **không liên quan đến việc hủy/chuyển hướng chuyến bay** — khác hẳn với kiểu thiếu có quy luật ở Mục 2.1. Đây là thiếu dữ liệu thật sự tại nguồn, cần xử lý riêng.

---

## 3. Cách thức làm sạch và chuẩn hóa — và cơ sở của từng lựa chọn

| # | Xử lý | Cách làm | Dựa vào đâu |
|---|---|---|---|
| 1 | Gộp ngày | Gộp `YEAR + MONTH + DAY` → cột `FLIGHT_DATE` (datetime). Không gộp `DAY_OF_WEEK` | `DAY_OF_WEEK` là giá trị suy ra được từ ngày, gộp vào sẽ dư thừa; giữ riêng để dùng làm feature cho mô hình có ý nghĩa hơn |
| 2 | Giải mã mã sân bay tháng 10 | Tra cứu mã số DOT Airport ID qua bảng chính thức `T_MASTER_CORD.csv` của BTS (`AIRPORT_ID → AIRPORT`), ánh xạ ngược về mã IATA | Phát hiện ở Mục 2.2: lỗi có quy luật rõ ràng (toàn bộ tháng 10) và có nguồn tra cứu chính thức (BTS) khớp 100% với các mã số xuất hiện trong dữ liệu → khôi phục được thay vì phải bỏ |
| 3 | Gắn cờ mã còn lại chưa xác định | Sau khi tra BTS, mã nào vẫn không khớp `airports.csv` → gắn `UNKNOWN` qua cột `..._VALID` (0/1) và `..._CLEAN` | Không xóa dòng vì các cột khác (giờ bay, độ trễ...) của cùng chuyến vẫn hợp lệ và có giá trị phân tích |
| 4 | Nhị phân hóa | `CANCELLED`, `DIVERTED`, `..._VALID` → kiểu `int` (0/1) thay vì `True/False` | Đưa thẳng vào mô hình học máy được, không cần bước encode thêm |
| 5 | Điền giá trị thiếu có điều kiện | 5 cột lý do trễ: điền `0` **chỉ cho chuyến không bị hủy**. `CANCELLATION_REASON`: điền `"NONE"`. `TAIL_NUMBER`: điền `"UNKNOWN"` | Theo đúng ý nghĩa xác định ở Mục 2.1 — chỉ điền khi `NaN` nghĩa là "không áp dụng", không áp dụng máy móc cho toàn bộ cột |
| 6 | Giữ nguyên `NaN` ở cột hậu chuyến bay | Không điền 0 hay giá trị ước lượng cho `DEPARTURE_TIME`, `ARRIVAL_TIME`, `TAXI_IN/OUT`... của chuyến bị hủy/chuyển hướng | Điền số 0 vào đây sẽ bị hiểu nhầm là "đúng giờ tuyệt đối", sai bản chất — sự kiện chưa từng xảy ra thì không nên có giá trị |
| 7 | Vá `SCHEDULED_TIME` | Tính lại **chính xác** = `SCHEDULED_ARRIVAL − SCHEDULED_DEPARTURE` (đổi giờ HHMM sang phút, dùng `% 1440` để tự xử lý bay qua đêm) | Đây là thiếu dữ liệu thật sự (Mục 2.3), nhưng 2 mốc giờ liên quan đều có sẵn nên tính lại được chính xác thay vì xóa dòng hoặc điền giá trị trung bình/ước lượng |
| 8 | Tạo biến mục tiêu `IS_DELAYED` | `1` nếu `ARRIVAL_DELAY ≥ 15` phút, `0` nếu đúng giờ/sớm, `NaN` nếu chuyến bị hủy | Chuẩn ngành hàng không định nghĩa "trễ" là từ 15 phút trở lên; chuyến bị hủy không có giá trị delay thực tế nên không thể gán 0 hay 1 |
| 9 | Cảnh báo rò rỉ dữ liệu (data leakage) | Ghi rõ danh sách cột chỉ có giá trị **sau khi bay xong** (`DEPARTURE_TIME`, `TAXI_OUT`, `AIR_TIME`, `ARRIVAL_TIME`...) | Nếu mục tiêu là dự đoán trễ chuyến **trước khi bay**, đưa các cột này vào mô hình sẽ khiến mô hình "nhìn thấy tương lai", làm sai lệch kết quả đánh giá |

---

## 4. Kết quả sau khi làm sạch

Sau khi chạy pipeline trên toàn bộ 5.819.079 dòng, dữ liệu đầu ra được kiểm tra lại (audit) theo từng phần để xác nhận tính đúng đắn:

| Hạng mục kiểm tra | Kết quả |
|---|---|
| Tổng số dòng | 5.819.079 (khớp dữ liệu gốc, không mất/thêm dòng) |
| Số cột | 37 (31 cột gốc + 6 cột phái sinh) |
| Dòng trùng lặp | 0 |
| Giá trị thiếu ở cột lý do trễ | 89.884 dòng — khớp chính xác với số chuyến bị hủy |
| Giá trị thiếu ở cột "hậu chuyến bay" | Khớp hợp lý với số chuyến hủy/chuyển hướng |
| `SCHEDULED_TIME` thiếu | 0 (đã vá xong) |
| Mã sân bay không hợp lệ sau khi tra BTS | Giảm từ 486.165 xuống chỉ còn phần rất nhỏ (các mã không tồn tại ở cả 2 bảng tra cứu, ví dụ mã `14027` bị chính BTS ghi nhầm) |
| Giá trị `DISTANCE` âm bất thường | 0 |
| Tỷ lệ chuyến bay trễ (`IS_DELAYED = 1`) | 18,3% (1.063.439 / 5.819.079 chuyến hoàn thành) |

**Cột phái sinh được thêm vào:** `FLIGHT_DATE`, `ORIGIN_AIRPORT_VALID`, `DEST_AIRPORT_VALID`, `ORIGIN_AIRPORT_CLEAN`, `DEST_AIRPORT_CLEAN`, `IS_DELAYED`.

**Kết luận:** dữ liệu `flights_cleaned.csv` đã sẵn sàng cho bước phân tích khám phá (EDA) và xây dựng mô hình học máy. Lưu ý duy nhất còn lại: khi dùng mô hình dự đoán delay trước chuyến bay, không sử dụng các cột thuộc nhóm "hậu chuyến bay" đã liệt kê ở Mục 3 (mục 9) để tránh rò rỉ dữ liệu.

---

## 5. Lọc riêng dữ liệu hãng bay DL (Delta Air Lines)

Ngoài file `flights_cleaned.csv` chứa toàn bộ dữ liệu, một bước lọc bổ sung được thực hiện để trích riêng dữ liệu của hãng Delta (mã `DL`), phục vụ phân tích chuyên sâu theo hãng nếu nhóm cần.

### 5.1. Cách thức thực hiện

- Đọc `flights_cleaned.csv` theo từng phần (chunk 500.000 dòng/lần) thay vì load toàn bộ vào bộ nhớ cùng lúc
- Lọc điều kiện `AIRLINE == "DL"` trên từng chunk
- Ghi kết quả nối tiếp ra file mới `flights_DL.csv`

### 5.2. Dựa vào đâu để làm cách đó

- File `flights_cleaned.csv` có kích thước gần 1GB (5,8 triệu dòng) — đọc theo chunk giúp script chạy được trên cả những máy có RAM hạn chế, tránh lỗi tràn bộ nhớ
- Lọc bằng đúng giá trị mã hãng (`AIRLINE == "DL"`) là cách chính xác nhất để tách riêng 1 hãng, không cần xử lý thêm vì cột `AIRLINE` đã sạch từ Phần 1 (không có mã lạ, không thiếu giá trị)

### 5.3. Kết quả

| Hạng mục | Kết quả |
|---|---|
| Tổng số dòng đọc vào | 5.819.079 |
| Số dòng thuộc hãng DL | 875.881 |
| Tỷ lệ | ~15,05% tổng dữ liệu |
| File kết quả | `flights_DL.csv` |
| Kiểm tra sau lọc | Cột `AIRLINE` trong file kết quả chỉ còn đúng 1 giá trị duy nhất: `DL` |
