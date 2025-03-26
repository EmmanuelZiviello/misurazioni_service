import datetime
# from flaskr import db
from F_taste_misurazioni.ma import ma
from marshmallow import post_load, post_dump, fields
from F_taste_misurazioni.models.misurazione import MisurazioneModel

class MisurazioneSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = MisurazioneModel
        load_instance = True
        # sqla_session = db.session

    valore = fields.Float(required=True)
    fk_paziente = fields.String(required=True)
    @post_load
    def lower_case(self, data, **kwargs):
        data['tipo_misurazione'] = data['tipo_misurazione'].lower()
        data['sorgente'] = data['sorgente'].lower()
        return data
    
misurazione_schema = MisurazioneSchema(only = ['valore','tipo_misurazione','sorgente', 'data_misurazione'])
misurazioni_schema = MisurazioneSchema(many = True, only = ['valore','tipo_misurazione','sorgente', 'data_misurazione'])


class MisurazioniAggregatedSchema(ma.Schema):
    misurazioni = fields.Nested(misurazioni_schema)

    @post_dump
    def aggregateByDay(self, data, **kwargs):
        aggregated_date = dict()
        for d in data['misurazioni']:
            date_key = datetime.datetime.strptime(d['data_misurazione'].split('T')[0], "%Y-%m-%d").strftime("%d-%m-%Y")
            if date_key not in aggregated_date:
                aggregated_date[date_key] = []
            aggregated_date[datetime.datetime.strptime(d['data_misurazione'].split('T')[0], "%Y-%m-%d").strftime("%d-%m-%Y")].append(d)
        return aggregated_date
    
class MisurazioniParamsSchema(ma.Schema):
    id_paziente = ma.String(required=True, allow_none=False)
    tipo_misurazione = ma.String(required=True, allow_none=False)
    inizio_periodo = ma.String(required=True, allow_none=False)
    fine_periodo = ma.String(required=True, allow_none=False)
    unit = ma.String(required=False, allow_none=True)