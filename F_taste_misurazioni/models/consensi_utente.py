from F_taste_misurazioni.db import Base
from sqlalchemy import Column, ForeignKey, Integer, String, Boolean
from sqlalchemy.orm import relationship


class ConsensiUtenteModel(Base):
    __tablename__ = "consensi_utente"

    id_consensi = Column(Integer, primary_key=True)
    storage_from_Google_fit = Column(Boolean, default=False)
    storage_from_Health_kit = Column(Boolean, default=False)
    condivisione_misurazioni_paziente = Column(Boolean, default=False)
    management_user_consent = Column(Boolean, default = False)
    statistic_user_consent = Column(Boolean, default = False)
    trainingAI_user_consent= Column(Boolean, default = False)
    fk_paziente = Column(String(7), 
                            ForeignKey("paziente.id_paziente", onupdate="CASCADE", ondelete="CASCADE"), 
                            nullable=False, 
                            unique = True)
    paziente = relationship("PazienteModel", back_populates='consensi_utente', lazy=True)

    def __init__(self, fk_paziente):
        self.fk_paziente = fk_paziente
        
        
    def __repr__(self):
        return 'ConsensiUtenteModel(fk_paziente=%r, storage_from_Google_fit=%r, storage_from_Health_kit=%r, condivisione_misurazioni_paziente=%r, management_user_consent=%r, statistic_user_consent=%r, trainingAI_user_consent=%r )' % (
                                                                                                       self.fk_paziente, 
                                                                                                       self.storage_from_Google_fit, 
                                                                                                       self.storage_from_Health_kit,
                                                                                                       self.condivisione_misurazioni_paziente,
                                                                                                       self.management_user_consent,
                                                                                                       self.statistic_user_consent,
                                                                                                       self.trainingAI_user_consent)

    def __json__(self):
        return { 'fk_paziente': self.fk_paziente, 
                'storage_from_Google_fit': self.storage_from_Google_fit, 
                'storage_from_Health_kit': self.storage_from_Health_kit,
                'condivisione_misurazioni_paziente': self.condivisione_misurazioni_paziente,
                'management_user_consent': self.management_user_consent,
                'statistic_user_consent' : self.statistic_user_consent,
                'trainingAI_user_consent' : self.trainingAI_user_consent
                }


  