from flask import render_template, request, session, redirect, url_for, flash
from . import bp
from .services import validate_user

@bp.route('/login', endpoint='login', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        # print(request.form)
        email = request.form.get('email')
        password = request.form.get('password')

        if not email or '@' not in email:
            flash('请输入有效的邮箱地址。', 'error')
        elif not password:
            flash('请输入密码。', 'error')
        elif validate_user(email, password):
            # print('login success')
            session['user'] = email # store user email in session
            return redirect(url_for('dataset.dataset_list')) # redirect to dataset list page
        else:
            flash('Invalid email or password', 'error')

    # 如果已经登录过了，不需要重复登录
    if session.get('user'):
        return redirect(url_for('index'))

    return render_template('auth/login.html')



@bp.route('/logout', endpoint='logout')
def logout():
    session.pop('user', None)  # 删除session数据
    return redirect(url_for('auth.login'))  # 重定向到登录页面




