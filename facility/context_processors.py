from django.conf import settings

# テンプレートへ変数を渡すには
# 1. view で渡す（毎回必要）
# 2. context processorで渡す（全体で必要な場合）


def global_settings(request):
    """プロジェクト共通のTextをtemplatesファイルで使えるように
    - context processorで渡す場合は、settings.pyのTEMPLATESのOPTIONSのcontext_processorsに登録する
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "facility.context_processors.global_settings",
            ],
    }
    """
    return {
        "VERSION_NO": settings.VERSION_NO,
        "DEBUG": settings.DEBUG,
        "DISPOSAL_SHOUKAKI": settings.DISPOSAL_SHOUKAKI,
    }
