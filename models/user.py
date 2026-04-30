class User:
    def __init__(self, user_id, first_name, last_name, email, password_hash, role="customer"):
        self.user_id = user_id
        self.first_name = first_name
        self.last_name = last_name
        self.email = email
        self.password_hash = password_hash
        self.role = role
        
    def get_full_name(self):
        return f"{self.first_name} {self.last_name}"