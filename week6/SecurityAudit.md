Báo cáo kiểm toán bảo mật - Music Social API
1. Giới thiệu
Báo cáo xác định 5 lỗ hổng bảo mật tiềm ẩn của Music Social API và đề xuất biện pháp khắc phục.
2. Các lỗ hổng bảo mật
2.1. Tấn công dò mật khẩu

Endpoint: POST /auth/login

Rủi ro: Kẻ tấn công thử nhiều mật khẩu để chiếm quyền truy cập tài khoản.

Khắc phục: Giới hạn số lần đăng nhập, tăng thời gian chờ sau nhiều lần thất bại và theo dõi hoạt động đáng ngờ.

2.2. Mật khẩu yếu

Endpoint: POST /auth/login

Rủi ro: Mật khẩu dễ đoán khiến tài khoản dễ bị chiếm đoạt.

Khắc phục: Ngăn sử dụng mật khẩu phổ biến, lưu mật khẩu bằng thuật toán băm an toàn và không lưu mật khẩu dưới dạng văn bản thuần.

2.3. Phát lại Refresh Token

Endpoint: POST /auth/refresh

Rủi ro: Kẻ tấn công sử dụng Refresh Token bị đánh cắp để lấy Access Token mới.

Khắc phục: Cấp Refresh Token mới sau mỗi lần sử dụng, phát hiện token bị sử dụng lại và thu hồi các token liên quan khi cần thiết.

2.4. Kiểm soát truy cập không đúng cách

Endpoint: GET /posts/{id}

Rủi ro: Người dùng thay đổi ID để truy cập bài viết riêng tư của người khác.

Khắc phục: Backend phải kiểm tra quyền truy cập và quyền riêng tư của từng bài viết.

2.5. Rò rỉ thông tin

Endpoint: Các API xác thực và lấy bài viết.

Rủi ro: Phản hồi lỗi tiết lộ thông tin tài khoản hoặc chi tiết nội bộ của hệ thống.

Khắc phục: Sử dụng thông báo lỗi phù hợp, không tiết lộ thông tin nhạy cảm và bảo vệ nhật ký hệ thống.
3. Kết luận
Backend cần triển khai và kiểm thử các biện pháp xác thực, phân quyền, giới hạn yêu cầu và bảo vệ token. Tệp OpenAPI chỉ mô tả yêu cầu bảo mật, không tự thực thi các biện pháp này.