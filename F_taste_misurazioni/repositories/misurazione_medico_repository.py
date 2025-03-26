from F_taste_misurazioni.models.misurazione_medico import MisurazioneMedicoModel
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session
from F_taste_misurazioni.db import get_session

class MisurazioneMedicoRepository:

    @staticmethod
    def get_last_misurazione_medico_of_paziente(id_paziente, session=None):
        session=session or get_session('dietitian')
        return session.query(MisurazioneMedicoModel).filter(MisurazioneMedicoModel.fk_paziente == id_paziente).order_by(MisurazioneMedicoModel.data_misurazione.desc()).first()

    @staticmethod
    def get_misurazione_medico_of_paziente_in_that_day(id_paziente, data_misurazione, session=None):
        session=session or get_session('dietitian')
        return (
            session.query(MisurazioneMedicoModel)
            .filter(
                MisurazioneMedicoModel.fk_paziente == id_paziente,
                MisurazioneMedicoModel.data_misurazione == data_misurazione
            )
            .first()
        )

    @staticmethod
    def save_misurazione(misurazione_medico, session=None):
        session=session or get_session('dietitian')
        try:
            session.add(misurazione_medico)
            session.commit()
        except SQLAlchemyError as e:
            session.rollback()


    
    @staticmethod
    def update_misurazione(misurazione_medico,updated_data ,session=None):
        session=session or get_session('dietitian')
        try:
            if misurazione_medico:
                for key,value in updated_data.items():
                    setattr(misurazione_medico,key,value)
            session.commit() 
        except SQLAlchemyError:
            session.rollback()
    

    @staticmethod
    def delete(misurazione_medico, session=None):
        session = session or get_session('dietitian')
        session.delete(misurazione_medico)
        session.commit()

    @staticmethod
    def get_misurazioni_medico_of_paziente(id_paziente,session=None):
        session=session or get_session('dietitian')
        # Eseguiamo una query per ottenere tutte le misurazioni medico associate a un paziente con id_paziente
        return session.query(MisurazioneMedicoModel).filter(MisurazioneMedicoModel.fk_paziente == id_paziente).all()
