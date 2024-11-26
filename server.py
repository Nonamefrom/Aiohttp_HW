import json

from aiohttp import web
from sqlalchemy.exc import IntegrityError

from models import Session, Advertisement, close_orm, init_orm

app = web.Application()


async def orm_context(app: web.Application):
    print("START")
    await init_orm()
    yield
    await close_orm()
    print("FINISH")


@web.middleware
async def session_middleware(request: web.Request, handler):
    async with Session() as session:
        request.session = session
        result = await handler(request)
        return result


app.cleanup_ctx.append(orm_context)
app.middlewares.append(session_middleware)


def get_http_error(error_cls, message):
    message = {"error": message}
    message = json.dumps(message)
    error = error_cls(text=message, content_type="application/json")
    raise error


async def get_advertisement_by_id(advertisement_id: int, session: Session) -> Advertisement:
    advertisement = await session.get(Advertisement, advertisement_id)
    if advertisement is None:
        raise get_http_error(web.HTTPNotFound, "Advertisement not found")
    return advertisement


async def delete_advertisement(advertisement: Advertisement, session: Session):
    await session.delete(advertisement)
    await session.commit()


async def add_advertisement(advertisement: Advertisement, session: Session):
    session.add(advertisement)
    try:
        await session.commit()
    except IntegrityError as err:
        raise get_http_error(web.HTTPConflict, "Advertisement already exists")


class AdvertisementView(web.View):

    @property
    def advertisement_id(self) -> int:
        return int(self.request.match_info["advertisement_id"])

    @property
    def session(self) -> Session:
        return self.request.session

    async def get(self):
        advertisement = await get_advertisement_by_id(self.advertisement_id, self.session)
        return web.json_response(advertisement.dict)

    async def post(self):
        data = await self.request.json()
        advertisement = Advertisement(**data)
        await add_advertisement(advertisement, self.session)
        return web.json_response(advertisement.dict_id)

    async def delete(self):
        advertisement = await get_advertisement_by_id(self.advertisement_id, self.session)
        await delete_advertisement(advertisement, self.session)
        return web.json_response({"status": "success"})


app.add_routes(
    [
        web.post(r"/advertisement", AdvertisementView),
        web.get(r"/advertisement/{advertisement_id:\d+}", AdvertisementView),
        web.delete(r"/advertisement/{advertisement_id:\d+}", AdvertisementView),
    ]
)

web.run_app(app)
