from app.secrets import api_config


def bearer_token_header():
    return {
        'Authorization': 'Bearer {}'.format(api_config['bearer_token'])
    }
