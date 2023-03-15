import string
import random

class PasswordManager:
    
  def __init__(self):
      self.generate_random_password()
    
  @property
  def password(self):
    return self._password
  
   # get random password pf length 8 with letters, digits, and symbols    
  def generate_random_password(self):
    characters = string.ascii_letters + string.digits + string.punctuation
    self._password = ''.join(random.choice(characters) for i in range(12))
    