""" Creates and provides access to a random;y generated password
"""
import string
import random

class PasswordManager:
    """ Creates and provides access to a random;y generated password
    """
    def __init__(self):
        self.generate_random_password()

    @property
    def password(self):
        """ Gets a randomly generated password

        Returns:
            string: Randomly generated password
        """
        return self._password

    def generate_random_password(self):
        """ Generate random password of length 12 with letters, digits, and symbols 
        """
        characters = string.ascii_letters + string.digits + string.punctuation
        self._password = ''.join(random.choice(characters) for i in range(12))
    