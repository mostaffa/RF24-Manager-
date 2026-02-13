from collections import defaultdict
import socketio
from http.cookies import SimpleCookie
from app.db.session import get_session
from app.core.security import get_current_user_from_token, extract_bearer_from_cookie_value

sio = socketio.AsyncServer(
    async_mode="asgi",
    cors_allowed_origins="*",
    logger=False,
    )
socket_app = socketio.ASGIApp(sio, socketio_path="/ws")

_user_sids = defaultdict(set)
_sid_user = {}

# connect event, if the user is authenticated, add them to a room based on their user ID or role
@sio.event
async def connect(sid, environ):
    print(f"\u001b[32mSocket Connection attempt: {sid}\u001b[0m")
    token_cookie = None
    headers = environ.get("asgi.scope", {}).get("headers", [])
    for k, v in headers:
        if k == b'cookie':
            c = SimpleCookie()
            try:
                c.load(v.decode('utf-8'))
            except Exception:
                break
            if 'access_token' in c:
                token_cookie = c['access_token'].value
            break

    # reject connection if no token cookie
    if not token_cookie:
        print(f"\u001b[31mConnection rejected (no token cookie): {sid}\u001b[0m")
        await sio.disconnect(sid)
        return False
    # get user info from token (you would implement this function to decode the JWT and fetch user info from DB)
    db = next(get_session())
    user_info = get_current_user_from_token(
        extract_bearer_from_cookie_value(token_cookie),
        db,
    )
    if not user_info:
        print(f"\u001b[31mConnection rejected (invalid token): {sid}\u001b[0m")
        await sio.disconnect(sid)
        return False
    
    print(user_info)
    # if user is valid, you can join them to a room based on their user ID or role
    await sio.save_session(sid, {"user_id": user_info.id})
    # join the user to his own room, his role room
    await sio.enter_room(sid, f"user_{user_info.id}")
    await sio.enter_room(sid, f"role_{user_info.role_id}")
    _user_sids[user_info.id].add(sid)
    _sid_user[sid] = user_info.id
    print(f"\u001b[32mSocket Connected: {sid} (User ID: {user_info.id})\u001b[0m")
    return True


@sio.event
async def disconnect(sid):
    user_id = _sid_user.pop(sid, None)
    if user_id is None:
        return
    _user_sids[user_id].discard(sid)
    if not _user_sids[user_id]:
        _user_sids.pop(user_id, None)


async def broadcast(event: str, data: dict) -> None:
    await sio.emit(event, data)


async def disconnect_user(user_id) -> None:
    sids = list(_user_sids.get(user_id, []))
    for sid in sids:
        await sio.disconnect(sid)