from flask import Blueprint

from views.availability import get_availability

blueprint = Blueprint('scheduling', __name__, url_prefix='/scheduling')

blueprint.add_url_rule(
    '/availability/',
    view_func=get_availability,
    methods=['GET'],
)