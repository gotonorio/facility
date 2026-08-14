from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission
from django.urls import reverse


# class PermissionRequiredViewTestBase(TestCase):
class PermissionRequiredViewTestMixin:
    """PermissionRequiredMixinを使用するViewの共通テスト"""

    url_name = None
    permission_codename = None
    permission_app_label = None

    @classmethod
    def setUpTestData(cls):
        """テストデータとして一度作ればよいもの"""
        User = get_user_model()

        # 一般ユーザー
        cls.normal_user = User.objects.create_user(
            username="normal_user",
            password="password123",
        )

        # 管理者ユーザー
        cls.manager_user = User.objects.create_user(
            username="manager_user",
            password="password123",
        )

        # Permission取得
        permission = Permission.objects.get(
            content_type__app_label=cls.permission_app_label,
            codename=cls.permission_codename,
        )

        cls.manager_user.user_permissions.add(permission)

    def setUp(self):
        """各テストの直前に準備したいもの"""
        self.url = reverse(self.url_name)

    def test_anonymous_user_redirects_to_login(self):
        """未ログインユーザーはログイン画面へリダイレクトされる"""

        response = self.client.get(self.url)

        self.assertRedirects(
            response,
            f"{reverse('register:login')}?next={self.url}",
        )

    def test_normal_user_is_forbidden(self):
        """Permissionを持たないユーザーは403になる"""

        self.client.force_login(self.normal_user)

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 403)

    def test_manager_user_can_access_view(self):
        """Permissionを持つユーザーはアクセスできる"""

        self.client.force_login(self.manager_user)

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)


class LoginRequiredViewTestMixin:
    """LoginRequiredMixinを使用するViewの共通テスト"""

    url_name = None

    @classmethod
    def setUpTestData(cls):
        """テストデータとして一度作ればよいもの"""
        User = get_user_model()

        cls.normal_user = User.objects.create_user(
            username="normal_user",
            password="password123",
        )

    def setUp(self):
        """各テストの直前に準備したいもの"""
        self.url = reverse(self.url_name)

    def test_anonymous_user_redirects_to_login(self):
        """未ログインユーザーはログイン画面へリダイレクトされる"""

        response = self.client.get(self.url)

        self.assertRedirects(
            response,
            f"{reverse('register:login')}?next={self.url}",
        )

    def test_logged_in_user_can_access_view(self):
        """ログインユーザーはViewへアクセスできる"""

        self.client.force_login(self.normal_user)

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)
