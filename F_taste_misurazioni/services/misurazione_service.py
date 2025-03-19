import datetime
import string
from flask import request
from flask_jwt_extended import get_jwt_identity
from flask_restx import Resource
from F_taste_misurazioni.db import get_session

from F_taste_misurazioni.schemas.misurazione import MisurazioneSchema
from F_taste_misurazioni.repositories.consensi_utente_repository import ConsensiUtenteRepository
from F_taste_misurazioni.repositories.misurazione_repository import MisurazioneRepository
from F_taste_misurazioni.repositories.nutrizionista_repository import NutrizionistaRepository
from F_taste_misurazioni.repositories.paziente_repository import PazienteRepository
from F_taste_misurazioni.namespaces import nutrizionista_ns
from F_taste_misurazioni.schemas.misurazione import misurazioni_schema, misurazione_schema,MisurazioniAggregatedSchema, MisurazioniParamsSchema
from F_taste_misurazioni.utils.management_utils import check_nutrizionista
from F_taste_misurazioni.kafka.kafka_producer import send_kafka_message
from F_taste_misurazioni.utils.kafka_helpers import wait_for_kafka_response
from flask_restx import reqparse



class MisurazioneService:
    @staticmethod
    def get_misurazioni(email_nutrizionista, request_args):
        validation_errors = MisurazioniParamsSchema().validate(request_args)
        if validation_errors:
            return validation_errors, 400

        session = get_session('dietitian')
        id_paziente = request_args['id_paziente']

        paziente = PazienteRepository.find_by_id(id_paziente, session)
        if paziente is None:
            session.close()
            return {'message': 'paziente non presente nel db'}, 404

        nutrizionista = NutrizionistaRepository.find_by_email(email_nutrizionista, session)
        if nutrizionista is None:
            session.close()
            return {"message":"nutrizionista non presente nel db"},404

        if not check_nutrizionista(paziente, nutrizionista):
            session.close()
            return {'message': 'paziente seguito da un altro nutrizionista'}, 403

        try:
            data_inizio = datetime.datetime.fromisoformat(request_args['inizio_periodo'])
            data_fine = datetime.datetime.fromisoformat(request_args['fine_periodo'])
        except ValueError:
            session.close()
            return {'message': 'not a valid datetime'}, 400

        consensi = ConsensiUtenteRepository.find_consensi_by_paziente_id(id_paziente, session)
        if not consensi.condivisione_misurazioni_paziente:
            session.close()
            return {'message': 'il paziente non ha accettato di condividere le misurazioni'}, 403

        misurazioni = MisurazioneRepository.find_by_paziente_and_period(
            id_paziente, request_args['tipo_misurazione'], data_inizio, data_fine, session
        )

        
        if misurazioni:
            if request_args.get('unit') == 'giorno':
                output_richiesta= MisurazioniAggregatedSchema().dump({'misurazioni': misurazioni}), 200
                session.close()
                return output_richiesta
            output_richiesta= misurazioni_schema.dump(misurazioni), 200
            session.close()
            return output_richiesta
        session.close()
        return [], 200
    
    @staticmethod
    def save_misurazione(misurazione_data,id_paziente):
        try:
            date = datetime.datetime.fromisoformat(misurazione_data['data_misurazione'])
        except ValueError:
            return {'message': 'not a valid date'}, 400
        #da capire sta questione di che schema usare
        validation_errors=misurazione_schema.validate(misurazione_data)
        if validation_errors:
            return validation_errors, 400
        message={"id_paziente":id_paziente}
        send_kafka_message("patient.existGet.request",message)
        response_paziente=wait_for_kafka_response(["patient.existGet.success", "patient.existGet.failed"])
        #controlli su response_paziente
        if response_paziente is None:
            return {"message": "Errore nella comunicazione con Kafka"}, 500
        
        if response_paziente.get("status_code") == "200":
            #####
            session = get_session('patient')
            if MisurazioneRepository.find_misurazione(id_paziente, misurazione_data['sorgente'],
                                                  misurazione_data['tipo_misurazione'], date, session) is not None:
                session.close()
                return {'message': 'misurazione già presente nel db'}, 409
            try:
                ## Non sicuro su queste due righe di codice,provare
                misurazione_schema_for_load = MisurazioneSchema(exclude = ['id_misurazione'])
                misurazione_data['fk_paziente']=id_paziente
                ## Non sicuro su queste due righe di codice, provare
                misurazione = misurazione_schema_for_load.load(misurazione_data)
                MisurazioneRepository.save_misurazione(misurazione, session)
                session.close()
                return {'message': 'misurazione salvata con successo'}, 201
            except Exception as e:
                print(f"Errore durante caricamento e creazione misurazione: {e}")
                session.rollback()
                session.close()
                return {'message': 'errore durante la creazione della misurazione'}, 409
            #######
        elif response_paziente.get("status_code") == "400":
            return {"esito save_misurazione":"Dati mancanti"}, 400
        elif response_paziente.get("status_code") == "404":
            return {"esito save_misurazione":"Paziente non presente nel db"}, 404

    '''
    @staticmethod
    def save_misurazione(misurazione_data,id_paziente):
        try:
            date = datetime.datetime.fromisoformat(misurazione_data['data_misurazione'])
        except ValueError:
            return {'message': 'not a valid date'}, 400
        
        misurazione_schema = MisurazioneSchema(exclude = ['id_misurazione'])

        validation_errors = misurazione_schema.validate(misurazione_data)
        if validation_errors:
            return validation_errors, 400

        session = get_session('patient')
        
        paziente = PazienteRepository.find_by_id(id_paziente, session)

        if paziente is None:
            session.close()
            return {'message': 'paziente non presente nel db'}, 404

        if MisurazioneRepository.find_misurazione(paziente.id_paziente, misurazione_data['sorgente'],
                                                  misurazione_data['tipo_misurazione'], date, session) is not None:
            session.close()
            return {'message': 'misurazione già presente nel db'}, 409

        try:
            misurazione = misurazione_schema.load(misurazione_data)
            misurazione.paziente = paziente
            MisurazioneRepository.save_misurazione(misurazione, session)
            session.close()
            return {'message': 'misurazione salvata con successo'}, 201
        except Exception:
            session.rollback()
            session.close()
            return {'message': 'errore durante la creazione della misurazione'}, 409
        '''
    
    @staticmethod
    def delete_misurazione(parametri_misurazione,id_paziente):
        validationError = MisurazioneSchema(only=['tipo_misurazione', 'data_misurazione']).validate(parametri_misurazione)

        if validationError:
            return validationError, 400

        try:
            date = datetime.datetime.fromisoformat(parametri_misurazione['data_misurazione'])
        except ValueError:
            return {'message': 'not a valid date'}, 400
        
        message={"id_paziente":id_paziente}
        send_kafka_message("patient.existGet.request",message)
        response_paziente=wait_for_kafka_response(["patient.existGet.success", "patient.existGet.failed"])
        #controlli su response_paziente
        if response_paziente is None:
            return {"message": "Errore nella comunicazione con Kafka"}, 500
        
        if response_paziente.get("status_code") == "200":
            #####
            session = get_session('patient')
            misurazione = MisurazioneRepository.find_misurazione_by_tipo_end_date(id_paziente,
                                                                                  parametri_misurazione['tipo_misurazione'].lower(),
                                                                                date, session)
            if misurazione:
                MisurazioneRepository.delete(misurazione, session)
                session.close()
                return {'message': 'misurazione eliminata con successo'}, 204
            else:
                session.close()
                return {'message': 'misurazione non presente nel db'}, 404
            
            #######
        elif response_paziente.get("status_code") == "400":
            return {"esito delete_misurazione":"Dati mancanti"}, 400
        elif response_paziente.get("status_code") == "404":
            return {"esito delete_misurazione":"Paziente non presente nel db"}, 404
        

    '''
    @staticmethod
    def delete_misurazione(parametri_misurazione,id_paziente):
        validationError = MisurazioneSchema(only=['tipo_misurazione', 'data_misurazione']).validate(parametri_misurazione)

        if validationError:
            return validationError, 400

        try:
            date = datetime.datetime.fromisoformat(parametri_misurazione['data_misurazione'])
        except ValueError:
            return {'message': 'not a valid date'}, 400

        session = get_session('patient')
        paziente = PazienteRepository.find_by_id(id_paziente, session)

        if paziente is None:
            session.close()
            return {'message': 'paziente non trovato'}, 404

        misurazione = MisurazioneRepository.find_misurazione_by_tipo_end_date(paziente.id_paziente,
                                                                                  parametri_misurazione['tipo_misurazione'].lower(),
                                                                                  date, session)

        if misurazione:
            MisurazioneRepository.delete(misurazione, session)
            session.close()
            return {'message': 'misurazione eliminata con successo'}, 204
        else:
            session.close()
            return {'message': 'misurazione non presente nel db'}, 404
        '''

    @staticmethod
    def update_misurazione(s_misurazione,id_paziente):
        try:
            old_date = datetime.datetime.fromisoformat(s_misurazione['old_data_misurazione'])
            datetime.datetime.fromisoformat(s_misurazione['data_misurazione'])
            del s_misurazione['old_data_misurazione']
        except ValueError:
            return {'message': 'not a valid date'}, 400
        validation_errors = misurazione_schema.validate(s_misurazione)
        if validation_errors:
            return validation_errors, 400
        
        message={"id_paziente":id_paziente}
        send_kafka_message("patient.existGet.request",message)
        response_paziente=wait_for_kafka_response(["patient.existGet.success", "patient.existGet.failed"])
        #controlli su response_paziente
        if response_paziente is None:
            return {"message": "Errore nella comunicazione con Kafka"}, 500
        
        if response_paziente.get("status_code") == "200":
            #####
            session = get_session('patient')
            misurazione_to_change = MisurazioneRepository.find_misurazione_by_tipo_end_date(
                id_paziente, s_misurazione['tipo_misurazione'].lower(), old_date, session
            )
            if misurazione_to_change is None:
                return {'message': 'misurazione non presente nel db'}, 404
            try:
                misurazione_schema_for_load = MisurazioneSchema(exclude = ['id_misurazione'])    
                updated_misurazione = misurazione_schema_for_load.load(s_misurazione)
                MisurazioneRepository.aggiorna_misurazione(misurazione_to_change, updated_misurazione, session)
                session.close()
                return {'message': 'misurazione aggiornata con successo'}, 201
            except Exception:
                session.close()
                return {'message': 'error'}, 500
            #######
        elif response_paziente.get("status_code") == "400":
            return {"esito update_misurazione":"Dati mancanti"}, 400
        elif response_paziente.get("status_code") == "404":
            return {"esito update_misurazione":"Paziente non presente nel db"}, 404
        
    '''
    @staticmethod
    def update_misurazione(misurazione_s,id_paziente):
        try:
            old_date = datetime.datetime.fromisoformat(misurazione_s['old_data_misurazione'])
            datetime.datetime.fromisoformat(misurazione_s['data_misurazione'])
            del misurazione_s['old_data_misurazione']
        except ValueError:
            return {'message': 'not a valid date'}, 400
        
        misurazione_schema = MisurazioneSchema(exclude=['id_misurazione'])
        validation_errors = misurazione_schema.validate(misurazione_s)
        if validation_errors:
            return validation_errors, 400
        
        session = get_session(role='patient')
        try:
            paziente = PazienteRepository.find_by_id(get_jwt_identity(), session)
            if paziente is None:
                return {'message': 'paziente non presente nel db'}, 404

            misurazione_to_change = MisurazioneRepository.find_misurazione_by_tipo_end_date(
                paziente.id_paziente, misurazione_s['tipo_misurazione'].lower(), old_date, session
            )

            if misurazione_to_change is None:
                return {'message': 'misurazione non presente nel db'}, 404

            updated_misurazione = misurazione_schema.load(misurazione_s)
            MisurazioneRepository.aggiorna_misurazione(misurazione_to_change, updated_misurazione, session)

            return {'message': 'misurazione aggiornata con successo'}, 201
        except Exception:
            return {'message': 'error'}, 500
        finally:
            session.close()
    '''

    @staticmethod
    def get_misurazioni_paziente(id_paziente,request_args):
        # Validazione dati
        try:
            data_inizio = datetime.datetime.fromisoformat(request_args['inizio_periodo'])
            data_fine = datetime.datetime.fromisoformat(request_args['fine_periodo'])
        except ValueError:
            return {'message': 'not a valid datetime'}, 400
        message={"id_paziente":id_paziente}
        send_kafka_message("patient.existGet.request",message)
        response_paziente=wait_for_kafka_response(["patient.existGet.success", "patient.existGet.failed"])
        #controlli su response_paziente
        if response_paziente is None:
            return {"message": "Errore nella comunicazione con Kafka"}, 500
        
        if response_paziente.get("status_code") == "200":
            #####
            session = get_session('patient')
            # Recupero misurazioni
            misurazioni = MisurazioneRepository.find_by_paziente_and_period(
                id_paziente,
                request_args['tipo_misurazione'].lower(),
                data_inizio,
                data_fine,
                session
            )

            if misurazioni:
                if 'unit' in request_args and request_args['unit'] == 'giorno':
                    output_richiesta= MisurazioniAggregatedSchema().dump({'misurazioni': misurazioni}), 200
                    session.close()
                    return output_richiesta
                
                output_richiesta= MisurazioneSchema(many=True).dump(misurazioni), 200
                session.close()
                return output_richiesta
            
            session.close()
            return [], 200

            #######
        elif response_paziente.get("status_code") == "400":
            return {"esito get_misurazioni_paziente":"Dati mancanti"}, 400
        elif response_paziente.get("status_code") == "404":
            return {"esito get_misurazioni_paziente":"Paziente non presente nel db"}, 404
        

    @staticmethod
    def get_misurazioni_paziente(id_paziente, request_args):
        # Validazione dati
        try:
            data_inizio = datetime.datetime.fromisoformat(request_args['inizio_periodo'])
            data_fine = datetime.datetime.fromisoformat(request_args['fine_periodo'])
        except ValueError:
            return {'message': 'not a valid datetime'}, 400

        session = get_session('patient')
        
        # Verifica che il paziente esista
        if PazienteRepository.find_by_id(id_paziente, session) is None:
            session.close()
            return {'message': 'paziente non presente nel db'}, 404
        
        # Recupero misurazioni
        misurazioni = MisurazioneRepository.find_by_paziente_and_period(
            id_paziente,
            request_args['tipo_misurazione'].lower(),
            data_inizio,
            data_fine,
            session
        )
        
        if misurazioni:
            if 'unit' in request_args and request_args['unit'] == 'giorno':
                output_richiesta= MisurazioniAggregatedSchema().dump({'misurazioni': misurazioni}), 200
                session.close()
                return output_richiesta
            
            output_richiesta= MisurazioneSchema(many=True).dump(misurazioni), 200
            session.close()
            return output_richiesta
        
        session.close()
        return [], 200