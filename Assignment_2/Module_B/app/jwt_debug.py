import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parent))
import auth_utils
import jwt

print('auth_utils.jwt module:', auth_utils.jwt)
print('auth_utils.jwt file:', getattr(auth_utils.jwt, '__file__', 'none'))
print('jwt module:', jwt)
print('jwt file:', getattr(jwt, '__file__', 'none'))
print('jwt version:', getattr(jwt, '__version__', 'unknown'))
print('JWT_SECRET', auth_utils.JWT_SECRET)

# Generate and validate token via auth_utils
print('\n-- auth_utils create/validate --')
tok = auth_utils.create_session(145, 'admin_alice', 'M001', 'admin')
print('token', tok)
payload, err = auth_utils.validate_session(tok)
print('payload', payload)
print('error', err)

# Direct decode with jwt imported separately
print('\n-- direct jwt decode --')
try:
    payload2 = jwt.decode(tok, auth_utils.JWT_SECRET, algorithms=['HS256'])
    print('direct decode ok', payload2)
except Exception as e:
    print('direct decode failed', type(e), e)
