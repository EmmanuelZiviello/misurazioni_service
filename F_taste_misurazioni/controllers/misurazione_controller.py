from flask import request
from flask_restx import Resource, fields
from flask_jwt_extended import get_jwt_identity
from F_taste_misurazioni.namespaces import nutrizionista_ns,paziente_ns
from F_taste_misurazioni.services.misurazione_service import MisurazioneService
from F_taste_misurazioni.utils.jwt_custom_decorators import nutrizionista_required,paziente_required
from F_taste_misurazioni.schemas.misurazione import MisurazioniParamsSchema

misurazione = paziente_ns.model('misurazione paziente model', {
    'valore' : fields.Float(required=True),
    'tipo_misurazione' : fields.String(required=True),
    'sorgente' : fields.String(required=True),
    'data_misurazione' : fields.DateTime(dt_format = 'iso8601', required=True)
}, strict = True)


misurazione_put = paziente_ns.model('misurazione put model', {
    'valore' : fields.Float(required=True),
    'tipo_misurazione' : fields.String(required=True),
    'sorgente' : fields.String(required=True),
    'data_misurazione' : fields.DateTime(dt_format = 'iso8601', required=True),
    'old_data_misurazione' : fields.DateTime(dt_format = 'iso8601', required=True)

}, strict=True)

class MisurazioniController(Resource):

    #da fare dopo la gestione di consensi utente in servizio separato
    @nutrizionista_required()
    @nutrizionista_ns.doc('ricevi misurazioni di un tipo scelto per un determinato periodo, il campo unit è opzionale', 
    params={
        'id_paziente': 'PAZ1234',
        'inizio_periodo': '2021-05-15',
        'fine_periodo': '2021-05-30',
        'tipo_misurazione': 'glucosio',
        'unit': 'giorno'
    }
)
    def get(self):
        email_nutrizionista = get_jwt_identity()
        request_args = request.args
        validation_errors = MisurazioniParamsSchema().validate(request_args)
        if validation_errors:
            return validation_errors, 400
        return MisurazioneService.get_misurazioni(email_nutrizionista, request_args)

class MisurazionePazienteController(Resource):
    
    @paziente_required()
    @paziente_ns.expect(misurazione)
    @paziente_ns.doc('post misurazione paziente')
    def post(self):
        misurazione_data = request.get_json()
        id_paziente = get_jwt_identity()
        return MisurazioneService.save_misurazione(misurazione_data,id_paziente)
    

    @paziente_required()
    @paziente_ns.doc('elimina misurazione paziente', params={'tipo_misurazione': 'glucosio', 'data_misurazione': '2023-01-01T00:00:00Z'})
    def delete(self):
        parametri_misurazione = request.args
        id_paziente = get_jwt_identity()
        return MisurazioneService.delete_misurazione(parametri_misurazione,id_paziente)
    
    
    @paziente_required()
    @paziente_ns.expect(misurazione_put)
    @paziente_ns.doc('aggiorna misurazione paziente')
    def put(self):
        misurazione_s = request.get_json()
        id_paziente = get_jwt_identity()
        return MisurazioneService.update_misurazione(misurazione_s,id_paziente)
    
class MisurazioniPazienteController(Resource):
    
    @paziente_required()
    @paziente_ns.doc('ricevi misurazioni di un tipo scelto per un determinato periodo',
                     params={'tipo_misurazione': 'BMI', 'inizio_periodo': '2021-05-15', 'fine_periodo': '2021-05-30'})
    def get(self):
        request_args = request.args

        # Validazione schema
        validation_errors = MisurazioniParamsSchema(exclude=['id_paziente']).validate(request_args)
        if validation_errors:
            return validation_errors, 400

        # Chiamata al service
        id_paziente = get_jwt_identity()
        return MisurazioneService.get_misurazioni_paziente(id_paziente, request_args)

        