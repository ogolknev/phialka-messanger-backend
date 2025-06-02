from fastapi import APIRouter, Response, Request, Depends

from auth.schemas import AuthDataBasic, AuthDataRefresh, TokenSet
from auth.use_caces import AuthUseCases
from auth.adapters import SQLAuthDataRepo, JWTManager

from utils.fastapi_jwt_auth import auth_scheme



import config



auth_routers = APIRouter(
    prefix = "/auth",
    tags = ["auth"]
)



auth_uc = AuthUseCases(
    repo=SQLAuthDataRepo(), 
    jwt_manager=JWTManager(
        key = config.JWT_SECRET_KEY, 
        access_ttl=config.JWT_ACCESS_TTL, 
        refersh_ttl=config.JWT_REFRESH_TTL
        )
    )



@auth_routers.post(
        "", 
        summary = 'Получить JWT токен по логину и паролю',
        response_model = TokenSet
        )
async def login(data: AuthDataBasic, res: Response):
    access, refresh = await auth_uc.get_jwt_by_logpass(data.username, data.password)
    res.set_cookie(
        key='access_token',
        value=access,
        secure=False,
        httponly=True,
        path='/'
    )
    res.set_cookie(
        key='refresh_token',
        value=refresh,
        secure=False,
        httponly=True,
        path='/auth/refresh'
    )

    return TokenSet(access=access, refresh=refresh)



@auth_routers.get(
        "/refresh", 
        summary = 'Получить JWT токен по refresh-токену',
        response_model = TokenSet,
        dependencies=[Depends(auth_scheme)]
        )
async def refresh_login(req: Request, res: Response):
    access, refresh = await auth_uc.refresh_jwt(req.cookies["refresh_token"])
    res.set_cookie(
        key='access_token',
        value=access,
        secure=False,
        httponly=True,
        path='/'
    )
    res.set_cookie(
        key='refresh_token',
        value=refresh,
        secure=False,
        httponly=True,
        path='/auth/refresh'
    )
    return TokenSet(access=access, refresh=refresh)
