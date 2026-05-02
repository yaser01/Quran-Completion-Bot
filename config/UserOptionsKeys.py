class UserOptionsKeys:
    My_Khatmas_Sort = "My_Khatmas_Sort"
    Public_Khatmas_Sort = "Public_Khatmas_Sort"

    @staticmethod
    def __getattributes__():
        return [attr for attr in UserOptionsKeys.__dict__
                if not attr.startswith('__')]
