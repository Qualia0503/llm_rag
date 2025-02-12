from flask import Blueprint, session, redirect, url_for


bp = Blueprint('dataset', __name__, url_prefix='/dataset', template_folder='../templates/')

@bp.before_request
def dataset_before_request():
    if 'user' not in session:
        return redirect(url_for('auth.login'))


from .views import dataset, document, segment