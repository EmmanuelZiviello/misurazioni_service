from F_taste_misurazioni.models.misurazione import MisurazioneModel
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session
from F_taste_misurazioni.db import get_session

class MisurazioneRepository:

    @staticmethod
    def find_misurazione(id_paziente, sorgente, tipo_misurazione, data, session=None):
        session=session or get_session('patient')
        return  session.query(MisurazioneModel).filter(
            MisurazioneModel.id_paziente == id_paziente,
            MisurazioneModel.sorgente == sorgente,
            MisurazioneModel.tipo_misurazione == tipo_misurazione,
            MisurazioneModel.data_misurazione == data
        ).first()


    @staticmethod
    def find_by_paziente_and_period(id_paziente, tipo_misurazione, data_inizio, data_fine, session=None):
        session=session or get_session('dietitian')
        return (
            session.query(MisurazioneModel)
            .filter_by(fk_paziente=id_paziente, tipo_misurazione=tipo_misurazione)
            .filter(MisurazioneModel.data_misurazione >= data_inizio)
            .filter(MisurazioneModel.data_misurazione <= data_fine)
            .order_by(MisurazioneModel.data_misurazione.asc())
            .all()
        )

    @staticmethod
    def find_misurazione_by_tipo_end_date(id_paziente, tipo_misurazione, data, session=None):
        session=session or get_session('patient')
        return session.query(MisurazioneModel).filter(
            MisurazioneModel.id_paziente == id_paziente,
            MisurazioneModel.tipo_misurazione == tipo_misurazione,
            MisurazioneModel.data_misurazione == data
        ).first()

    @staticmethod
    def get_last_misurazione_of_paziente(id_paziente, session=None):
        session=session or get_session('dietitian')
        return session.query(MisurazioneModel).filter(MisurazioneModel.id_paziente == id_paziente).order_by(MisurazioneModel.data_misurazione.desc()).first()

    @staticmethod
    def get_misurazione_of_paziente_in_that_day(id_paziente, data_misurazione, session=None):
        session=session or get_session('dietitian')
        return (
            session.query(MisurazioneModel)
            .filter(
                MisurazioneModel.id_paziente == id_paziente,
                MisurazioneModel.data_misurazione == data_misurazione
            )
            .first()
        )

    @staticmethod
    def save_misurazione(misurazione, session=None):
        session=session or get_session('patient')
        try:
            session.add(misurazione)
            session.commit()
        except SQLAlchemyError as e:
            session.rollback()


    
    @staticmethod
    def update_misurazione(misurazione,updated_data ,session=None):
        session=session or get_session('patient')
        try:
            if misurazione:
                for key,value in updated_data.items():
                    setattr(misurazione,key,value)
            session.commit() 
            return misurazione
        except SQLAlchemyError:
            session.rollback()
            return None
    

    @staticmethod
    def delete(misurazione, session=None):
        session = session or get_session('patient')
        session.delete(misurazione)
        session.commit()

    @staticmethod
    def get_misurazioni_of_paziente(paziente,session=None):
        session=session or get_session('dietitian')
        return paziente.misurazioni if paziente else None

    @staticmethod
    def aggiorna_misurazione(misurazione_to_change, updated_misurazione, session=None):
        session=session or get_session('patient')
        misurazione_to_change.data_misurazione = updated_misurazione.data_misurazione
        misurazione_to_change.valore = updated_misurazione.valore
        session.add(misurazione_to_change)
        session.commit()