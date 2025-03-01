# python 3 headers, required if submitting to Ansible
from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

DOCUMENTATION = """
name: get_password
lookup: get_password
author: Daniel Lynch <daniel.lynch2016@gmail.com>
version_added: "0.1.1"
short_description: Get password from Passbolt
description:
    - This lookup returns a list of passwords from Passbolt.
options:
  name:
    description:
      - The name of the password in passbolt.
    required: true
  username:
    description:
      - The username field of the password. Use this to narrow down your search if there are multiple passwords with the same name.
    required: false
  passbolt_uri:
    description:
      - The Passbolt instance Fully Qualified Domain Name(FQDN)
    required: true
  passphrase:
    description:
      - The Passphrase used with the GPG Private key used to access Passbolt.
    required: true
  gpgkey:
    description:
      - The GPG Private key used to access Passbolt.
    required: true
  return_format:
    description:
      - Controls how passwords are returned.
      - C(dict) returns a list of dictionaries that includes the password name, username, uri, description,
      - C(password) returns a list of just the passwords
    choices:
      - dict
      - password
    default: password
"""
EXAMPLES = """
- name: Get list of passwords with the name Testing
  ansible.builtin.debug:
    msg: "{{ lookup('daniel_lynch.passbolt.get_password', 'Testing', gpgkey=gpgkey, passphrase=passphrase, passbolt_uri=passbolt_uri) }}"
- name: Get list of passwords with the name Testing and username Test
  ansible.builtin.debug:
    msg: "{{ lookup('daniel_lynch.passbolt.get_password', 'Testing', username='Test', gpgkey=gpgkey, passphrase=passphrase, passbolt_uri=passbolt_uri) }}"
- name: Get list of password dictionaries with the name Testing
  ansible.builtin.debug:
    msg: "{{ lookup('daniel_lynch.passbolt.get_password', 'Testing', return_format='dict', gpgkey=gpgkey, passphrase=passphrase, passbolt_uri=passbolt_uri) }}"
"""

from ansible.errors import AnsibleError, AnsibleParserError
from ansible.plugins.lookup import LookupBase
from ansible.utils.display import Display


display = Display()


HAS_MODULE = False
try:
    from passbolt.passbolt import passbolt
    HAS_MODULE = True
except ImportError:
    HAS_MODULE = False

class LookupModule(LookupBase):

    def run(self, terms, variables=None, **kwargs):

      if not HAS_MODULE:
          raise AnsibleError("Please pip install passbolt to use the passbolt get_password lookup module.")

      display.vvvv("Init")
      gpgkey = None
      passphrase = None
      passbolt_uri = None
      username = None
      return_format = "password"

      for key, value in kwargs.items():
        if key == "username":
          username = value
        if key == "return_format":
          if value == "dict":
            return_format = "dict"
        if key == "gpgkey":
          gpgkey = value
        if key == "passphrase":
          passphrase = value
        if key == "passbolt_uri":
          passbolt_uri = value

      Passbolt = passbolt(gpgkey, passphrase, passbolt_uri)
      display.vvvv("Logged into Passbolt")
      ret = []
      for term in terms:
          passwords = Passbolt.getpassword(term, username)
          display.vvvv("Got password(s)")
          if passwords:
            for password in passwords:
              if return_format == "dict":
                ret.append(password.__dict__)
              if return_format == "password":
                ret.append(password.password)
          else:
            raise AnsibleError("Could not locate password for: %s" % term)

      return ret