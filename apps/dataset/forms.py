# apps/dataset/forms.py
from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, IntegerField
from wtforms.validators import DataRequired, Length, NumberRange

class DatasetForm(FlaskForm):
    name = StringField(
        "知识库名称",
        validators=[
            DataRequired(message="知识库名称是必填项。"), 
            Length(max=20, message="知识库名称不能超过20个字符。")
        ],
    )
    desc = TextAreaField(
        "知识库描述",
        validators=[
            DataRequired(message="知识库描述是必填项。"), 
            Length(max=200, message="知识库描述不能超过200个字符。")
        ],
    )


class SegmentForm(FlaskForm):
    content = TextAreaField(
        "内容",
        validators=[
            DataRequired(message="内容是必填项。"),
            Length(min=5, max=2000, message="内容必须在5到2000个字符之间。")
        ],
    )
    order = IntegerField(
        "排序",
        validators=[
            DataRequired(message="排序是必填项。"),
            NumberRange(min=1, message="排序必须是一个正整数。")
        ],
    )