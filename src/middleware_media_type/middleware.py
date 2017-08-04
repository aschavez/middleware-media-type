import falcon
import json
import os
import uuid
import schematics
from falcon_exceptions import HTTPException
from dicttoxml import dicttoxml
from datetime import datetime, date
from decimal import Decimal

_schematics_base_version = schematics.__version__.split('.')[0]
if int(_schematics_base_version) >= 2:
    from schematics.datastructures import FrozenDict
    from schematics.exceptions import ConversionError, ValidationError


class _JSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime):
            return obj.strftime('%Y-%m-%dT%H:%M:%SZ')
        elif isinstance(obj, date):
            return obj.strftime('%Y-%m-%d')

        return json.JSONEncoder.default(self, obj)


def _body_parser(data):
    if int(_schematics_base_version) >= 2:
        if isinstance(data, FrozenDict):
            new_data = {}
            for k, v in data.iteritems():
                new_data.update({ k: _body_parser(v) })
            return new_data
        elif isinstance(data, ConversionError):
            return str(data[0])
        elif isinstance(data, ValidationError):
            return str(data[0])
    if isinstance(data, list):
        new_data = []
        for item in data:
            new_data.append(_body_parser(item))
        return new_data
    elif isinstance(data, dict):
        new_data = {}
        for k, v in data.iteritems():
            new_data.update({ k: _body_parser(v) })
        return new_data
    elif isinstance(data, datetime):
        return data.strftime('%Y-%m-%dT%H:%M:%SZ')
    elif isinstance(data, date):
        return data.strftime('%Y-%m-%d')
    elif isinstance(data, uuid.UUID):
        return str(data)
    elif isinstance(data, Decimal):
        return str(data)
    else:
        return data

    
class RequireJSON(object):

    def process_request(self, req, resp):
        if not req.client_accepts_json and not req.client_accepts_xml:
            msg = "This API only supports requests encoded as JSON or XML"
            status = 415
            resp.status = str(status)
            resp.body = {
                "status": str(status),
                "devMessage": msg,
                "userMessage": msg
            }
        if req.method in ('POST', 'PUT'):
            if 'application/json' not in req.content_type:
                msg = "This API only supports requests encoded as JSON"
                status = 415
                resp.status = str(status)
                resp.body = {
                    "status": str(status),
                    "devMessage": msg,
                    "userMessage": msg
                }


class ParseMediaType(object):

    _parse_type = None

    def process_request(self, req, resp):
        path, ext = os.path.splitext(req.path)
        self._parse_type = ext.lstrip(".") if ext else None

    def process_response(self, req, resp, resource):
        response = resp.body
        content_type = resp.content_type


        if resp.body == None:
            if req.method != "OPTIONS":
                raise falcon.HTTPMethodNotAllowed(allowed_methods=["GET", "POST"],
                    title='This API does not support that route or method.',
                    description='http://developer.rcp.pe/api/json')
        else:
            resp.body = _body_parser(resp.body)
            if not ( type(resp.body) == type(dict()) ):
                try:
                    resp.body = json.loads(resp.body)
                except:
                    raise HTTPException(406,
                        "This API only supports responses encoded as JSON or XML",
                        "This API only supports responses encoded as JSON or XML")

            if req.client_accepts_xml:
                content_type = "application/xml"
                response = dicttoxml(resp.body)

            if req.client_accepts_json or self._parse_type == "json":
                content_type = "application/json"
                response = json.dumps(resp.body, cls=_JSONEncoder)

            if self._parse_type == "xml":
                content_type = "application/xml"
                response = dicttoxml(resp.body)

            resp.content_type = content_type
            resp.body = response
