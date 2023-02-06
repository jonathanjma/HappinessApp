from api.app import ma
from api.models import Happiness
from marshmallow import post_dump

# put marshmallow API schemas here (for API request/response documentation)


class HappinessSchema(ma.SQLAlchemySchema):
    class Meta:
        model = Happiness

    id = ma.auto_field(dump_only=True)
    value = ma.auto_field(required=True)
    comment = ma.auto_field()
    timestamp = ma.Str(required=True)

    @post_dump
    def fix_time(self, data, **kwargs):
        data['timestamp'] = data['timestamp'].split()[0]
        return data


class HappinessPutSchema(ma.Schema):
    value = ma.Int()
    comment = ma.Str()


class HappinessGetTime(ma.Schema):
    user_id = ma.Int(required=True)
    start = ma.Str()
    end = ma.Str()


class HappinessGetCount(ma.Schema):
    user_id = ma.Int(required=True)
    page = ma.Int()
    count = ma.Int()
