from F_taste_misurazioni.ma import ma
# from flaskr import db
from F_taste_misurazioni.models.nutrizionista import NutrizionistaModel
from marshmallow import fields

class NutrizionistaSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = NutrizionistaModel
        load_instance = True
        # sqla_session = db.session
    
    email = fields.Email(required=True)