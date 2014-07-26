# -*-*- encoding: utf-8 -*-*-

import sys
import json
import datetime
import uuid
import hashlib
import urllib2

from flask.ext.wtf import TextField, PasswordField, Required, URL, ValidationError

from labmanager.forms import AddForm
from labmanager.rlms import register, Laboratory, Capabilities
from labmanager.rlms.base import BaseRLMS, BaseFormCreator, Versions

def get_module(version):
    """get_module(version) -> proper module for that version

    Right now, a single version is supported, so this module itself will be returned.
    When compatibility is required, we may change this and import different modules.
    """
    # TODO: check version
    return sys.modules[__name__]

class UnrAddForm(AddForm):

    DEFAULT_LOCATION = 'Rosario, Argentina'
    DEFAULT_URL = 'http://labremf4a.fceia.unr.edu.ar/about/'

    remote_login = TextField("Login",        validators = [Required()])
    password     = PasswordField("Password")
    remote_url   = TextField("FCEIA URL", default = "http://labremf4a.fceia.unr.edu.ar/accesodeusto.aspx", validators = [Required(), URL(False)])

    def __init__(self, add_or_edit, *args, **kwargs):
        super(UnrAddForm, self).__init__(*args, **kwargs)
        self.add_or_edit = add_or_edit

    @staticmethod
    def process_configuration(old_configuration, new_configuration):
        old_configuration_dict = json.loads(old_configuration)
        new_configuration_dict = json.loads(new_configuration)
        if new_configuration_dict.get('password', '') == '':
            new_configuration_dict['password'] = old_configuration_dict.get('password','')
        return json.dumps(new_configuration_dict)

    def validate_password(form, field):
        if form.add_or_edit and field.data == '':
            raise ValidationError("This field is required.")

class UnrFormCreator(BaseFormCreator):

    def get_add_form(self):
        return UnrAddForm

FORM_CREATOR = UnrFormCreator()

class RLMS(BaseRLMS):

    def __init__(self, configuration):
        self.configuration = json.loads(configuration or '{}')

        self.login    = self.configuration.get('remote_login')
        self.password = self.configuration.get('password')
        self.remote_url = self.configuration.get('remote_url')
        
        if self.login is None or self.password is None or self.remote_url is None:
            raise Exception("Laboratory misconfigured: fields missing" )

    def get_version(self):
        return Versions.VERSION_1

    def get_capabilities(self):
        return [ Capabilities.WIDGET ] 

    def get_laboratories(self):
        return [ Laboratory('unr-physics', 'unr-physics', autoload = True) ]

    def reserve(self, laboratory_id, username, institution, general_configuration_str, particular_configurations, request_payload, user_properties, *args, **kwargs):

        dtime = datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")

        random_str = uuid.uuid4()
        data       = "username=%(username)s&fullname=%(fullname)s&timestamp=%(timestamp)s&random=%(random)s" % {
            'username'  : username,
            'fullname'  : username,
            'timestamp' : dtime,
            'random'    : random_str,
        }
        crypted   = _rc4(data, self.password)
        data_hash = hashlib.new("md5", data).hexdigest()
        tpl       = '%(URL)s?id_instalacion=%(INSTALLATION)s&cadena=%(DATA)s&checksum=%(HASH)s'

        url = tpl %  {
            'URL'          : self.remote_url, 
            'INSTALLATION' : self.login,
            'DATA'         : crypted.encode('hex'), 
            'HASH'         : data_hash,
        }

        return {
            'reservation_id' : urllib2.quote(url),
            'load_url' : url
        }

    def list_widgets(self, laboratory_id, **kwargs):
        return [ dict(name = u'UNR_FCEIA', description = u'UNR FCEIA Physics remote laboratory', height = '900px') ]

    def load_widget(self, reservation_id, widget_name, **kwargs):
        return {
            'url' : urllib2.unquote(reservation_id)
        }

def _rc4(data, key):
    """
    Encrypts the data with key key using RC4. Based on the pseudocode presented in:

    Using the http://en.wikipedia.org/wiki/ARC4 
    """
    # The key-scheduling algorithm (KSA)
    S = range(256)
    j = 0
    for i in xrange(256):
        j = ( j + S[i] + ord(key[i % len(key)]) ) % 256

        S[i], S[j] = S[j], S[i]

    # The pseudo-random generation algorithm (PRGA)
    i = 0
    j = 0
    output = []

    for c in data:
        i = (i + 1) % 256
        j = (j + S[i]) % 256

        S[i], S[j] = S[j], S[i]

        k = ord(c) ^ S[ (S[i] + S[j]) % 256]
        output.append( chr(k) )

    return ''.join(output)


register("FCEIA-UNR", ['1.0'], __name__)

