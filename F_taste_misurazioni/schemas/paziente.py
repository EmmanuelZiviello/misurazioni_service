import re
# from flaskr import db
from F_taste_misurazioni.ma import ma
from F_taste_misurazioni.models.paziente import PazienteModel
from marshmallow import ValidationError, fields, validates

class PazienteSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = PazienteModel
        load_instance = True
        # sqla_session = db.session
        include_fk = True

    email = fields.Email(required=True)
    data_nascita = fields.Date(required=False)
    sesso = fields.Boolean(required=False)
    fk_nutrizionista = fields.Integer(required=True)

    @validates('password')
    def is_a_strong_password(self, value):
        pattern = re.compile(r"^(?=.*?[A-Z])(?=.*?[a-z])(?=.*?[0-9])(?=.*?[#?!@$%^&*-]).{8,20}$")

        if not pattern.match(value) :
            raise ValidationError("la password non è abbastanza sicura")


