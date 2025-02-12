def validate_user(email, password):
    # 这里使用硬编码的用户数据进行验证，生产项目中需要用数据库维护邮箱和密码
    valid_users = {
        'admin@outlook.com': '123789'
    }
    if email in valid_users and valid_users[email] == password:
        return True
    return False