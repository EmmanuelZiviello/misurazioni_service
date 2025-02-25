from F_taste_misurazioni.models.consensi_utente import ConsensiUtenteModel
from F_taste_misurazioni.models.log_consensi import LOGConsensi
from F_taste_misurazioni.db import get_session
from sqlalchemy.exc import SQLAlchemyError

class ConsensiUtenteRepository:

    @staticmethod
    def find_consensi_by_paziente_id(paziente_id, session=None):
        session = session or get_session('patient')
        return session.query(ConsensiUtenteModel).filter_by(fk_paziente=paziente_id).first()



    @staticmethod
    def save_consensi(consensi_utente, session=None):
        session = session or get_session('patient')
        session.add(consensi_utente)
        session.commit()

  


    @staticmethod
    def update_consensi(consensi_paziente, updated_data, session=None):
        session = session or get_session('patient')
        try:
            if consensi_paziente:
                for key, value in updated_data.items():
                    setattr(consensi_paziente, key, value)
                session.commit()
                return consensi_paziente
            return None
        except SQLAlchemyError:
            session.rollback()
            return None  