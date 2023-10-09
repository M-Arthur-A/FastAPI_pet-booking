from fastapi import Depends, Request, status
from jose import jwt, JWTError
from datetime import datetime

from app.config import settings
from app.users.repo import UsersDAO
from app.exceptions import IncorrectTokenFormatException, TokenAbsentException, TokenExpiredException, UserIsNotPresentException


def get_token(request: Request):
    token = request.cookies.get("booking_access_token")
    if not token:
        raise TokenAbsentException
    return token

async def get_current_user(token: str = Depends(get_token)):
    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            settings.ALGORYTM,
        )
    except JWTError:
        raise IncorrectTokenFormatException

    # ключ exp автоматически проверяется
    # командой jwt.decode, поэтому отдельно проверять это не нужно
    # expire: str = str(payload.get('exp'))
    # if (not expire) or (int(expire) < datetime.utcnow().timestamp()):
    #     raise TokenExpiredException

    user_id: str = str(payload.get('sub'))
    if not user_id:
        raise UserIsNotPresentException

    user = await UsersDAO.find_by_id(int(user_id))
    if not user:
        raise UserIsNotPresentException

    return user
