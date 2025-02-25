from F_taste_misurazioni.db import get_session
from F_taste_misurazioni.models.nutrizionista import NutrizionistaModel

class NutrizionistaRepository:

  

    @staticmethod
    def find_by_id(id_nutrizionista, session=None):
        session = session or get_session('dietitian')
        return session.query(NutrizionistaModel).filter_by(id_nutrizionista=id_nutrizionista).first()

    @staticmethod
    def find_by_email(email, session=None):
        session = session or get_session('dietitian')
        return session.query(NutrizionistaModel).filter_by(email=email).first()

    @staticmethod
    def add(nutrizionista, session=None):
        session = session or get_session('dietitian')
        session.add(nutrizionista)
        session.commit()

    @staticmethod
    def delete(nutrizionista, session=None):
        session = session or get_session('dietitian')
        session.delete(nutrizionista)
        session.commit()

  
        
   