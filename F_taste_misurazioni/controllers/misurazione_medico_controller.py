from flask import request
from flask_restx import Resource, fields
from flask_jwt_extended import get_jwt_identity
from F_taste_misurazioni.namespaces import nutrizionista_ns,paziente_ns
from F_taste_misurazioni.services.misurazione_medico_service import MisurazioneMedicoService
from F_taste_misurazioni.utils.jwt_custom_decorators import nutrizionista_required,paziente_required
from F_taste_misurazioni.schemas.misurazione_medico import MisurazioneMedicoSchema

post_misurazione_model = nutrizionista_ns.model('misurazione medico da aggiungere', {
    'peso': fields.Integer,
    'altezza': fields.Integer,
    'vita': fields.Integer,
    'fianchi': fields.Integer,
    'bmi': fields.Float,
    'trigliceridi': fields.Float,
    'colesterolo_DHL': fields.Float,
    'glucosio': fields.Float,
    'pressione_sistole': fields.Float,
    'pressione_diastole': fields.Float,
    'data_misurazione': fields.String("format yyyy-MM-dd"),
    'massa_magra': fields.Integer,
    'massa_grassa': fields.Integer,
    'idratazione': fields.Integer,
    'menopausa': fields.Boolean,
    'fk_paziente': fields.String,
})


put_misurazione_medico = nutrizionista_ns.model('paziente da ricevere misurazioni medico', {
    'peso' : fields.Integer,
    'altezza' : fields.Integer,
    'vita'  : fields.Integer,
    'fianchi' : fields.Integer,
    'bmi' : fields.Float,
    'trigliceridi' : fields.Float,
    'colesterolo_DHL' : fields.Float,
    'glucosio' : fields.Float,
    'pressione_sistole' : fields.Float,
    'pressione_diastole' : fields.Float,
    'data_misurazione' : fields.String("format yyyy-MM-dd"),
    'old_data_misurazione' : fields.String("format yyyy-MM-dd"),
    'massa_magra' : fields.Integer,
    'massa_grassa' : fields.Integer,
    'idratazione' : fields.Integer,
    'menopausa' : fields.Boolean,
    'fk_paziente' : fields.String,
}, strict=True)


misurazione_medico_schema = MisurazioneMedicoSchema(only = [
    'peso',
    'altezza',
    'vita',
    'fianchi',
    'bmi',
    'trigliceridi',
    'colesterolo_DHL',
    'glucosio',
    'pressione_sistole',
    'pressione_diastole',
    'data_misurazione',
    'massa_magra',
    'massa_grassa',
    'idratazione',
    'menopausa',
    'fk_paziente'])

class MisurazioneMedicoController(Resource):
    #da provare
    @nutrizionista_required()
    @nutrizionista_ns.expect(post_misurazione_model)
    @nutrizionista_ns.doc('crea misurazione')
    def post(self):
        parametri_misurazione = request.get_json()
        email_nutrizionista = get_jwt_identity()
        return MisurazioneMedicoService.crea_misurazione(parametri_misurazione, email_nutrizionista)
    #
    @nutrizionista_required()
    @nutrizionista_ns.expect(put_misurazione_medico)
    @nutrizionista_ns.doc('modifica una misurazione')
    def put(self):
        parametri_misurazione = request.get_json()
        email_nutrizionista = get_jwt_identity()

        validation_errors = misurazione_medico_schema.validate(parametri_misurazione)
        if validation_errors:
            return validation_errors, 400

        return MisurazioneMedicoService.update_misurazione(parametri_misurazione, email_nutrizionista)
    
    #
    @nutrizionista_required()
    @nutrizionista_ns.doc('ricevi misurazione medico in una data', params={'id_paziente': 'PAZ1234', 'data_misurazione': '2022-10-11'})
    def get(self):
        request_args = request.args
        email_nutrizionista = get_jwt_identity()
        
        return MisurazioneMedicoService.get_misurazione_medico(
            email_nutrizionista, 
            request_args.get('id_paziente'), 
            request_args.get('data_misurazione')
            )
        
    #   
    @nutrizionista_required()
    @nutrizionista_ns.doc('misurazione da eliminare', params={'id_paziente': 'PAZ1234', 'data_misurazione': '2023-01-01T00:00:00Z'})
    def delete(self):
        request_args = request.args
        email_nutrizionista = get_jwt_identity()
        
        return  MisurazioneMedicoService.delete_misurazione_medico(
            email_nutrizionista, 
            request_args.get('id_paziente'), 
            request_args.get('data_misurazione')
        )

class MisurazioniMedicoController(Resource):
    @nutrizionista_required()
    @nutrizionista_ns.doc('ricevi tutte le misurazioni di un paziente', params={'id_paziente': 'PAZ1234'})
    def get(self):
        request_args = request.args
        email_nutrizionista = get_jwt_identity()

        return MisurazioneMedicoService.get_misurazioni_paziente(
            email_nutrizionista,
            request_args.get("id_paziente")
        )

class MisurazioniMedicoPazienteController(Resource):
    @paziente_required()
    @paziente_ns.doc('richiedi l\'ultima misurazione effettuata dal medico')
    def get(self):
        if request.args:
            return { 'message': 'unexpected field' }, 400
        
        id_paziente = get_jwt_identity()
        return MisurazioneMedicoService.get_last_misurazione_medico(id_paziente)
        