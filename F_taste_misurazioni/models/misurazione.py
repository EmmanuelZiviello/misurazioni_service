from F_taste_misurazioni.db import Base
from sqlalchemy_utils import StringEncryptedType
from F_taste_misurazioni.utils.credentials import get_key
from sqlalchemy import Column, Integer, String, UniqueConstraint, TIMESTAMP, Float, ForeignKey
from sqlalchemy.orm import relationship, scoped_session



class MisurazioneModel(Base):
    __tablename__ = "misurazione"
    id_misurazione = Column(Integer, primary_key=True)
    valore = Column(StringEncryptedType(Float, get_key))
    tipo_misurazione = Column(StringEncryptedType(String, get_key))
    sorgente = Column(StringEncryptedType(String, get_key))
    fk_paziente = Column(String(10),
                            ForeignKey("paziente.id_paziente", onupdate="CASCADE", ondelete="CASCADE"), 
                            nullable=False)
    data_misurazione = Column(TIMESTAMP)
    paziente = relationship("PazienteModel", back_populates='misurazioni', lazy=True)
    __table_args__ = (UniqueConstraint(data_misurazione, fk_paziente, tipo_misurazione, sorgente, name="one_type_of_for_that_time"),)

    def __init__(self, valore, data_misurazione, tipo_misurazione, sorgente):
        self.valore = valore
        self.data_misurazione = data_misurazione
        self.tipo_misurazione = tipo_misurazione
        self.sorgente = sorgente

    def __repr__(self):
        return 'MisurazioneModel(valore=%s, data_misurazione=%s, tipo_misurazione=%s, sorgente=%s)' % (self.valore, self.data_misurazione, self.tipo_misurazione, self.sorgente)

    def __json__(self):
        return { 'valore' : self.valore, 'data_misurazione' : self.data_misurazione, 'tipo_misurazione' : self.tipo_misurazione , 'sorgente' : self.sorgente}
    