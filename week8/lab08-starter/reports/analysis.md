lab4
1. Trong 3 kịch bản, kịch bản nào có p95 cao nhất? Vì sao?
Kịch bản C (200 users) có p95 cao nhất là 160 ms.
Nguyên nhân:
- Lượng người dùng tăng quá nhanh: Chỉ trong 4 giây có 200 người dùng cùng truy cập, tạo ra gần 100 request mỗi giây.
- Kẹt khi ghi dữ liệu vào SQLite: Ở mức 10 đến 50 user, hệ thống xử lý dư sức nên độ trễ gần như không đổi.
- Đến mức 200 user, nhiều người cùng thêm sách mới khiến SQLite phải khóa file để ghi từng cái một, làm thời gian chờ tăng vọt.



2. Có endpoint nào fail rate tăng theo số user? Đoán nguyên nhân dựa trên code.
Thực tế đo được:
- Tất cả các lỗi trong 3 lần chạy đều nằm ở endpoint GET /books?year={year}.
- Tỷ lệ lỗi này rất thấp (khoảng 0.3% đến 0.6%) và không tăng lên khi tăng số user.
- Các API còn lại đều đạt 0% lỗi.

Nguyên nhân:
- Dự đoán nếu tăng tải cao hơn nữa (app.py): Vì server dùng SQLite và chạy ở chế độ mặc định, nếu tiếp tục tăng thêm user, POST /books sẽ bị lỗi thật đầu tiên.
- Khi nhiều luồng tranh nhau ghi vào cùng một file SQLite, server sẽ báo lỗi 500 (database is locked).



3. Nếu prod cần SLO p95 < 300ms, kịch bản nào đạt? Đề xuất baseline cho CI gate.
p95 < 300ms:
- Cả 3 kịch bản A, B và C đều đạt yêu cầu này (26 ms, 27 ms và 160 ms đều nhỏ hơn 300 ms).
- Ngay cả API chậm nhất ở kịch bản C là POST /books (270 ms) vẫn nằm dưới ngưỡng 300 ms.

Đề xuất cấu hình chuẩn (Baseline) cho CI gate:
- Lệnh chạy tự động: Cho chạy kịch bản tải trung bình với 50 users trong 30 giây:
  locust -f performance/locustfile.py --headless -H http://127.0.0.1:5000 -u 50 -r 10 -t 30s
- Điều kiện đạt (Pass):
  - Thời gian phản hồi p95 < 150 ms (thấp hơn một nửa so với mức 300 ms thực tế để đảm bảo an toàn).
  - Tỷ lệ lỗi <= 1.5% (chỉ cho phép sai số nhỏ quanh mức 1% lỗi giả lập, có lỗi thật từ server là chặn ngay).



Câu hỏi bonus: Nếu connection pool giới hạn 5, điều gì xảy ra khi 200 user truy cập đồng thời? Làm thế nào để xác nhận bằng Locust?
Điều gì xảy ra:
- Trong cùng một thời điểm, chỉ có tối đa 5 người dùng được kết nối với database để xử lý dữ liệu.
- 195 người còn lại phải đứng xếp hàng chờ tới lượt.
- Thời gian phản hồi (p95 và Max) sẽ tăng vọt vì mất quá nhiều thời gian nằm chờ kết nối trống.
- Nếu chờ quá 30 giây (mức timeout mặc định của SQLAlchemy), hệ thống sẽ báo lỗi TimeoutError và trả về hàng loạt lỗi 500.

Xác nhận bằng Locust:
- Mở file báo cáo HTML của Locust và xem biểu đồ Response Times: đường p95 sẽ tăng dựng đứng theo số lượng user.
- Nhìn sang biểu đồ Total Requests per Second (RPS): đường này sẽ đi ngang và không tăng thêm được nữa do bị nghẽn ở 5 kết nối.
- Kiểm tra bảng Failures: sau khoảng 30 giây kể từ lúc đạt 200 user, bảng này sẽ hiện hàng loạt lỗi HTTP 500 ở các API có truy vấn database.