import markdown
from django import template
from django.conf import settings
from django.utils.safestring import mark_safe

register = template.Library()

"""
facilityアプリケーション用カスタムテンプレートタグ・フィルタ.
    - facility/settings.pyのTEMPLATES設定に以下を追加すること。
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "facility.context_processors.global_settings",
            ],
            "libraries": {},
        },
"""


@register.simple_tag
def url_replace(request, field, value):
    """GETパラメータを一部を置き換える.
    paginate処理とgetパラメータの同時使用を許すためのページ処理用templateタグ。
    """
    url_dict = request.GET.copy()
    url_dict[field] = str(value)
    return url_dict.urlencode()


@register.filter
def markdown_to_html(text):
    """マークダウンをhtmlに変換する。
    https://python-markdown.github.io/reference/#extensions
    """
    html = markdown.markdown(text, extensions=settings.MARKDOWN_EXTENSIONS)
    return mark_safe(html)


@register.filter
def using(using):
    """表示変更フィルタ"""
    ret = "空き"
    if using:
        ret = "使用中"
    return ret


@register.filter
def multi(value, arg):
    """掛け算."""
    return int(value * arg)


@register.filter
def subtract(value, arg):
    """引き算用フィルタ"""
    return value - arg


@register.filter(name="is_in_group")
def is_in_group(user, group_name):
    """
    ユーザーが特定のグループに属している場合にTrueを返すテンプレートフィルタ
    """
    if user.groups.filter(name=group_name).exists():
        return True
    return False
