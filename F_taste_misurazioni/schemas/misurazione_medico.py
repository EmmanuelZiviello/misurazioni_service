# from flaskr import db
from F_taste_misurazioni.ma import ma
from F_taste_misurazioni.models.misurazione_medico import MisurazioneMedicoModel
from marshmallow import fields

class MisurazioneMedicoSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = MisurazioneMedicoModel
        load_instance = True
        include_fk = True
        # sqla_session = db.session


    peso = fields.Integer(required=True)
    altezza = fields.Integer(required=True)
    vita = fields.Integer(required=True)
    fianchi = fields.Integer(required=True)
    bmi = fields.Float(required=True)
    trigliceridi = fields.Float(required=True)
    colesterolo_DHL = fields.Float(required=True)
    glucosio = fields.Float(required=True)
    pressione_sistole = fields.Float(required=True)
    pressione_diastole = fields.Float(required=True)
    data_misurazione = fields.Date(required=True)
    menopausa = fields.Boolean(required=True)
    massa_magra = fields.Integer(required=True)
    massa_grassa = fields.Integer(required=True)
    idratazione = fields.Integer(required=True)
    fk_paziente = fields.String(required=True)
