from fastapi.security import OAuth2PasswordBearer

oauth2_scheme = OAuth2PasswordBearer("/api/oauth2/token")
