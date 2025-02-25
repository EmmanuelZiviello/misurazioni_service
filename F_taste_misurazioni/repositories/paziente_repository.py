from F_taste_misurazioni.db import get_session
from F_taste_misurazioni.models.paziente import PazienteModel
from F_taste_misurazioni.models.nutrizionista import NutrizionistaModel
from sqlalchemy.exc import SQLAlchemyError

class PazienteRepository:

    @staticmethod
    def find_by_email(email, session=None):
        session = session or get_session('patient')
        return session.query(PazienteModel).filter_by(email=email).first()

    @staticmethod
    def find_by_id(id_paziente, session=None):
        session = session or get_session('patient')
        return session.query(PazienteModel).filter_by(id_paziente=id_paziente).first()

    @staticmethod
    def add(paziente, session=None):
        session = session or get_session('patient')
        session.add(paziente)
        session.add(paziente.consensi_utente)#forse necessario dato che viene creato insieme al paziente
        session.commit()

    @staticmethod
    def delete(paziente, session=None):
        session = session or get_session('patient')
        session.delete(paziente)
        session.commit()


    
       

 
        


   
