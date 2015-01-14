innvent-sso-python-client
=========================

Cliente python para o SSO da Innvent


Instalando o client
-------------------

Para isso basta instalar o client ao projeto:

```shell
pip install git+ssh://git@github.com/innvent/innvent-sso-python-client.git#egg=innvent_sso_client
```

Depois adicione as configurações necessarias ao settings da aplicação:

```python
SSO_SERVICE_TOKEN = 'seu_token_do_sso' # 'brmed'
SSO_SECRET_KEY = 'sua_secret_key_do_sso' # 'd3f2091230d0d02d636e91901f314d98bd1fd8e3'
SSO_HOST = 'host_do_sso_do_ambiente' # 'https://sso.grupobrmed.com.br'

INSTALLED_APPS += ('innvent_sso_client',)
AUTHENTICATION_BACKENDS += ('innvent_sso_client.backends.SSOBackend',)
MIDDLEWARE_CLASSES += ('innvent_sso_client.middlewares.SSOMiddleware',)
```
