from typing import Union

from flask import Flask, jsonify, request
from flask.views import MethodView
from flask_bcrypt import Bcrypt
from pydantic import ValidationError
from sqlalchemy.exc import DisconnectionError, IntegrityError

from models import Session, Advertisement
from shema import CreateAdvertisement, DeleteAdvertisement

app = Flask("advertisements")
bcrypt = Bcrypt(app)


class HttpError(Exception):

    def __init__(self, status_code, message):
        self.status_code = status_code
        self.message = message


@app.errorhandler(HttpError)
def error_handler(error: HttpError):
    response = jsonify({"error": error.message})
    response.status_code = error.status_code
    return response


def validate(schema_cls: type[CreateAdvertisement], json_data):
    try:
        return schema_cls(**json_data).dict(exclude_unset=True)
    except ValidationError as err:
        errors = err.errors()
        for error in errors:
            error.pop("ctx", None)
        raise HttpError(400, errors)


@app.before_request
def before_requests():
    session = Session()
    request.session = session


@app.after_request
def after_request(http_response):
    request.session.close()
    return http_response


# def add_Advertisement(advertisement):
#     request.session.add(advertisement)
#     try:
#         request.session.commit()
#     except IntegrityError as er:
#         raise HttpError(409, "Advertisement already exist")

def add_Advertisement(advertisement):
    existing_advertisement = (
        request.session.query(Advertisement)
        .filter_by(
            heading=advertisement.heading,
            description=advertisement.description,
            owner=advertisement.owner
        )
        .first()
    )
    if existing_advertisement is not None:
        raise HttpError(409, "Advertisement with the same heading, description, and owner already exists")
    request.session.add(advertisement)
    try:
        request.session.commit()
    except IntegrityError:
        raise HttpError(409, "Error saving Advertisement to the database")


def get_Advertisement_by_id(advertisement_id) -> Advertisement:
    advertisement = request.session.get(Advertisement, advertisement_id)
    if advertisement is None:
        raise HttpError(404, "Advertisement not found")
    return advertisement


class AdvertisementView(MethodView):
    def get(self, advertisement_id: int):
        advertisement = get_Advertisement_by_id(advertisement_id)
        return jsonify(advertisement.dict)

    def post(self):
        json_data = validate(CreateAdvertisement, request.json)
        advertisement = Advertisement(
            heading=json_data["heading"],
            description=json_data["description"],
            owner=json_data["owner"]
        )
        add_Advertisement(advertisement)
        return jsonify(advertisement.dict)

    def delete(self, advertisement_id: int):
        advertisement = get_Advertisement_by_id(advertisement_id)
        request.session.delete(advertisement)
        request.session.commit()
        return jsonify({"status": "deleted"})


Advertisement_view = AdvertisementView.as_view("Advertisement")

app.add_url_rule(
    "/advertisement/<int:advertisement_id>", view_func=Advertisement_view, methods=["GET", "DELETE"]
)
app.add_url_rule("/advertisement", view_func=Advertisement_view, methods=["POST"])
app.run()
