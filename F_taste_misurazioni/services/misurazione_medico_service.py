from F_taste_misurazioni.db import get_session
from F_taste_misurazioni.repositories.paziente_repository import PazienteRepository
from F_taste_misurazioni.repositories.nutrizionista_repository import NutrizionistaRepository
from F_taste_misurazioni.schemas.misurazione_medico import MisurazioneMedicoSchema
from F_taste_misurazioni.utils.management_utils import check_nutrizionista
from F_taste_misurazioni.kafka.kafka_producer import send_kafka_message
from F_taste_misurazioni.utils.kafka_helpers import wait_for_kafka_response
from F_taste_misurazioni.repositories.misurazione_medico_repository import MisurazioneMedicoRepository
from sqlalchemy.exc import IntegrityError

misurazione_medico_schema = MisurazioneMedicoSchema()


misurazione_medico_schema_for_dump = MisurazioneMedicoSchema(only = [
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



class MisurazioneMedicoService:


    @staticmethod 
    def crea_misurazione(parametri_misurazione,email_nutrizionista):
        validation_errors = misurazione_medico_schema.validate(parametri_misurazione)
        if validation_errors:
            return validation_errors, 400
        id_paziente=parametri_misurazione["fk_paziente"]
        message={"id_paziente":id_paziente}
        send_kafka_message("patient.existGet.request",message)
        response_paziente=wait_for_kafka_response(["patient.existGet.success", "patient.existGet.failed"])
        #controlli su response_paziente
        if response_paziente is None:
            return {"message": "Errore nella comunicazione con Kafka"}, 500
        
        if response_paziente.get("status_code") == "200":
            paziente_id_nutrizionista=response_paziente["id_nutrizionista"]
            if paziente_id_nutrizionista:
                #invia tramite kafka per capire se è presente il nutrizionista nel db e riceve il suo id
                message={"email_nutrizionista":email_nutrizionista}
                send_kafka_message("dietitian.existGet.request",message)
                response_nutrizionista=wait_for_kafka_response(["dietitian.existGet.success", "dietitian.existGet.failed"])
                #controlli su response_nutrizionista
                if response_nutrizionista is None:
                    return {"message": "Errore nella comunicazione con Kafka"}, 500
                
                if response_nutrizionista.get("status_code") == "200":
                    id_nutrizionista=response_nutrizionista["id_nutrizionista"]

                    if id_nutrizionista:
                    #   
                        if paziente_id_nutrizionista == id_nutrizionista:
                                #####
                                session = get_session('dietitian')
                                
                                misurazione = misurazione_medico_schema.load(parametri_misurazione)
                                if MisurazioneMedicoRepository.get_misurazione_medico_of_paziente_in_that_day(id_paziente, misurazione.data_misurazione, session):
                                    session.close()
                                    return {'message': 'esiste già una misurazione per questa data'}, 409
                                MisurazioneMedicoRepository.save_misurazione(misurazione, session)
                                session.close()
                                return {"esito richiesta":"Misurazione medico creata con successo"}, 200
                                #######
                        else:
                            return {'message': 'paziente non seguito'}, 403
                        
                    else:
                        return{"message":"Id nutrizionista mancante"}, 400
                    #
                elif response_nutrizionista.get("status_code") == "400":
                    return {"esito crea_misurazione":"Dati mancanti"}, 400
                elif response_nutrizionista.get("status_code") == "404":
                    return {"esito crea_misurazione":"Nutrizionista non presente nel db"}, 404
            
            return{"message":"Il paziente non è seguito da un nutrizionista"}, 403

            
        elif response_paziente.get("status_code") == "400":
            return {"esito crea_misurazione":"Dati mancanti"}, 400
        elif response_paziente.get("status_code") == "404":
            return {"esito crea_misurazione":"Paziente non presente nel db"}, 404


    '''
    @staticmethod
    def crea_misurazione(parametri_misurazione, email_nutrizionista):
        session = get_session('dietitian')

        validation_errors = misurazione_medico_schema.validate(parametri_misurazione)
        if validation_errors:
            return validation_errors, 400

        paziente = PazienteRepository.find_by_id(parametri_misurazione['fk_paziente'], session)
        if not paziente:
            session.close()
            return {'message': 'id paziente non presente nel db'}, 404

        nutrizionista = NutrizionistaRepository.find_by_email(email_nutrizionista, session)
        if not nutrizionista:
            session.close()
            return {'message': 'email nutrizionista non presente nel db'}, 404

        if not check_nutrizionista(paziente, nutrizionista):
            session.close()
            return {'message': 'paziente seguito da un altro nutrizionista'}, 403

        misurazione = misurazione_medico_schema.load(parametri_misurazione)
        if MisurazioneMedicoRepository.get_misurazione_medico_of_paziente_in_that_day(paziente.id_paziente, misurazione.data_misurazione, session):
            session.close()
            return {'message': 'esiste già una misurazione per questa data'}, 409

        misurazione.paziente = paziente
        MisurazioneMedicoRepository.save_misurazione(misurazione, session)
        session.close()
        return {"esito richiesta":"Misurazione medico creata con successo"},200
    '''
    @staticmethod
    def update_misurazione(parametri_misurazione, email_nutrizionista):
        session = get_session('dietitian')

        # Recupero paziente
        paziente = PazienteRepository.find_by_id(parametri_misurazione['fk_paziente'], session)
        if paziente is None:
            session.close()
            return {'message': 'id paziente non presente nel db'}, 404

        # Recupero nutrizionista
        nutrizionista = NutrizionistaRepository.find_by_email(email_nutrizionista, session)
        if nutrizionista is None:
            session.close()
            return {'message': 'email nutrizionista non presente nel db'}, 404

        if not check_nutrizionista(paziente, nutrizionista):
            session.close()
            return {'message': 'paziente seguito da un altro nutrizionista'}, 403

        # Recupero misurazione
        old_data_misurazione = parametri_misurazione['data_misurazione']
        misurazione_medico = MisurazioneMedicoRepository.get_misurazione_medico_of_paziente_in_that_day(
            paziente.id_paziente, old_data_misurazione, session
        )

        if misurazione_medico is None:
            session.close()
            return {'message': 'misurazioneMedico non presente nel db'}, 404

        # Aggiornamento misurazione
        try:
            misurazione_medico.paziente = paziente
            misurazione_medico=MisurazioneMedicoRepository.update_misurazione(misurazione_medico,parametri_misurazione ,session)
            if misurazione_medico is None:
                session.close()
                return {'message': 'misurazioneMedico non presente nel db'}, 404
            
            session.close()
            return {"message":"misurazione medico aggiornata con successo"},200

        except IntegrityError:
            session.rollback()
            session.close()
            return {'message': 'esiste già una misurazione per questa data'}, 409
        

    @staticmethod
    def get_misurazione_medico(email_nutrizionista,id_paziente,data_misurazione):
        message={"id_paziente":id_paziente}
        send_kafka_message("patient.existGet.request",message)
        response_paziente=wait_for_kafka_response(["patient.existGet.success", "patient.existGet.failed"])
        #controlli su response_paziente
        if response_paziente is None:
            return {"message": "Errore nella comunicazione con Kafka"}, 500
        
        if response_paziente.get("status_code") == "200":
            paziente_id_nutrizionista=response_paziente["id_nutrizionista"]
            if paziente_id_nutrizionista:
                #invia tramite kafka per capire se è presente il nutrizionista nel db e riceve il suo id
                message={"email_nutrizionista":email_nutrizionista}
                send_kafka_message("dietitian.existGet.request",message)
                response_nutrizionista=wait_for_kafka_response(["dietitian.existGet.success", "dietitian.existGet.failed"])
                #controlli su response_nutrizionista
                if response_nutrizionista is None:
                    return {"message": "Errore nella comunicazione con Kafka"}, 500
                
                if response_nutrizionista.get("status_code") == "200":
                    id_nutrizionista=response_nutrizionista["id_nutrizionista"]

                    if id_nutrizionista:
                    #   
                        if paziente_id_nutrizionista == id_nutrizionista:
                                #####
                                session = get_session('dietitian')
                                misurazione_medico=MisurazioneMedicoRepository.get_misurazione_medico_of_paziente_in_that_day(id_paziente,data_misurazione,session)
                                if misurazione_medico is None:
                                    return {'message': 'misurazione medico non presente nel db'}, 404
                                output_richiesta=misurazione_medico_schema_for_dump.dump(misurazione_medico)
                                session.close()
                                return output_richiesta, 200
                                #######
                        else:
                            return {'message': 'paziente non seguito'}, 403
                        
                    else:
                        return{"message":"Id nutrizionista mancante"}, 400
                    #
                elif response_nutrizionista.get("status_code") == "400":
                    return {"esito get_misurazione":"Dati mancanti"}, 400
                elif response_nutrizionista.get("status_code") == "404":
                    return {"esito get_misurazione_medico":"Nutrizionista non presente nel db"}, 404
            
            return{"message":"Il paziente non è seguito da un nutrizionista"}, 403

            
        elif response_paziente.get("status_code") == "400":
            return {"esito get_misurazione_medico":"Dati mancanti"}, 400
        elif response_paziente.get("status_code") == "404":
            return {"esito get_misurazione_medico":"Paziente non presente nel db"}, 404

    '''
    @staticmethod
    def get_misurazione_medico(email_nutrizionista, id_paziente, data_misurazione):
        session = get_session('dietitian')
        
        try:
            paziente = PazienteRepository.find_by_id(id_paziente, session)
            if paziente is None:
                return {'message': 'id paziente non presente nel db'}, 404

            nutrizionista = NutrizionistaRepository.find_by_email(email_nutrizionista, session)
            if nutrizionista is None:
                return {'message': 'email nutrizionista non presente nel db'}, 404

            if check_nutrizionista(paziente, nutrizionista):
                misurazione_medico = MisurazioneMedicoRepository.get_misurazione_medico_of_paziente_in_that_day(paziente.id_paziente, data_misurazione, session)
                
                if misurazione_medico is None:
                    return {'message': 'misurazione medico non presente nel db'}, 404
                
                return misurazione_medico_schema_for_dump.dump(misurazione_medico), 200
            else:
                return {'message': 'paziente seguito da un altro nutrizionista'}, 403
        
        finally:
            session.close()
    '''

    @staticmethod
    def delete_misurazione_medico(email_nutrizionista, id_paziente, data_misurazione):
        session = get_session('dietitian')

        try:
            paziente = PazienteRepository.find_by_id(id_paziente, session)
            if paziente is None:
                return {'message': 'id paziente non presente nel db'}, 404

            nutrizionista = NutrizionistaRepository.find_by_email(email_nutrizionista, session)
            if nutrizionista is None:
                return {'message': 'email nutrizionista non presente nel db'}, 404

            if check_nutrizionista(paziente, nutrizionista):
                misurazione_medico = MisurazioneMedicoRepository.get_misurazione_medico_of_paziente_in_that_day(paziente.id_paziente, data_misurazione, session)
                
                if misurazione_medico is None:
                    return {'message': 'misurazione medico non presente nel db'}, 404
                
                MisurazioneMedicoRepository.delete(misurazione_medico, session)
                return {'message': 'misurazione medico eliminata con successo'}, 200
            
            return {'message': 'paziente seguito da un altro nutrizionista'}, 403
        
        finally:
            session.close()



    @staticmethod
    def get_misurazioni_paziente(email_nutrizionista, id_paziente):
        session = get_session('dietitian')

        try:
            paziente = PazienteRepository.find_by_id(id_paziente, session)
            if paziente is None:
                return {'message': 'paziente non presente nel db'}, 404

            nutrizionista = NutrizionistaRepository.find_by_email(email_nutrizionista, session)
            if nutrizionista is None:
                return {'message': 'email nutrizionista non presente nel db'}, 404

            if check_nutrizionista(paziente, nutrizionista):
                misurazioni = MisurazioneMedicoRepository.get_misurazioni_medico_of_paziente(paziente)
                misurazioni_medico_schema = MisurazioneMedicoSchema(many=True)
                return misurazioni_medico_schema.dump(misurazioni), 200

            return {'message': 'paziente non seguito'}, 403

        finally:
            session.close()

    @staticmethod
    def get_last_misurazione_medico(id_paziente):
        session = get_session('patient')
        
        paziente_data = PazienteRepository.find_by_id(id_paziente, session)
        if paziente_data is None:
            session.close()
            return { 'message': 'paziente non presente nel db' }, 404
        
        last_misurazione = MisurazioneMedicoRepository.get_last_misurazione_medico_of_paziente(id_paziente, session)
        session.close()

        if last_misurazione is not None:
            output_richiesta= misurazione_medico_schema.dump(last_misurazione), 200
            session.close()
            return output_richiesta
        else:
            session.close()
            return {}, 204