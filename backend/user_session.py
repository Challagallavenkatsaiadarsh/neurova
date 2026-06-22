class UserSession:
    user_id = None
    email = None
    token = None

    @classmethod
    def login(cls, user_id, email, token=None):
        cls.user_id = user_id
        cls.email = email
        cls.token = token

    @classmethod
    def logout(cls):
        cls.user_id = None
        cls.email = None
        cls.token = None
