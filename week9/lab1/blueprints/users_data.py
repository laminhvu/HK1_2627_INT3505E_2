USERS = {
    1: {"first_name": "Tuấn", "last_name": "Đào", "email": "a@vnu.vn"},
    2: {"first_name": "Đào", "last_name": "Minh Tuấn", "email": "b@vnu.vn"},
}
def get_user(uid):
    return USERS.get(uid)
