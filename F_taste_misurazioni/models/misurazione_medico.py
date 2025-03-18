from F_taste_misurazioni.db import Base
from sqlalchemy_utils import StringEncryptedType
from F_taste_misurazioni.utils.credentials import get_key
from sqlalchemy import Column, Float, String, Integer, ForeignKey, Boolean, Date, UniqueConstraint
from sqlalchemy.orm import relationship

class MisurazioneMedicoModel(Base):
    __tablename__ = "misurazione_medico"
    id_misurazione = Column(Integer, primary_key=True)
    peso = Column(StringEncryptedType(Integer, get_key))
    altezza = Column(StringEncryptedType(Integer, get_key))
    vita = Column(StringEncryptedType(Integer, get_key))
    fianchi = Column(StringEncryptedType(Integer, get_key))
    bmi = Column(StringEncryptedType(Float, get_key))
    trigliceridi = Column(StringEncryptedType(Float, get_key))
    colesterolo_DHL = Column(StringEncryptedType(Float, get_key))
    glucosio = Column(StringEncryptedType(Float, get_key))
    pressione_sistole = Column(StringEncryptedType(Float, get_key))
    pressione_diastole = Column(StringEncryptedType(Float, get_key))
    data_misurazione = Column(Date, nullable=False)
    menopausa = Column(StringEncryptedType(Boolean, get_key))
    massa_magra = Column(StringEncryptedType(Integer, get_key))
    massa_grassa = Column(StringEncryptedType(Integer, get_key))
    idratazione = Column(StringEncryptedType(Integer, get_key))
    fk_paziente = Column(String(7), nullable=False)  # Eliminata la ForeignKey
    __table_args__ = (UniqueConstraint(data_misurazione, fk_paziente, name="one_measurements_for_day"),)

    def __init__(self, peso, altezza, vita, fianchi, bmi, trigliceridi, colesterolo_DHL, glucosio,
                 pressione_sistole, pressione_diastole, data_misurazione, menopausa, fk_paziente, massa_magra,
                 massa_grassa, idratazione):
        self.peso = peso
        self.altezza = altezza
        self.vita = vita
        self.fianchi = fianchi
        self.bmi = bmi
        self.trigliceridi = trigliceridi
        self.colesterolo_DHL = colesterolo_DHL
        self.glucosio = glucosio
        self.pressione_sistole = pressione_sistole
        self.pressione_diastole = pressione_diastole
        self.data_misurazione = data_misurazione
        self.menopausa = menopausa
        self.fk_paziente = fk_paziente
        self.massa_magra = massa_magra
        self.massa_grassa = massa_grassa
        self.idratazione = idratazione

    def __repr__(self):
        return 'MisurazioneMedicoModel(id_misurazione=%s, peso=%s, altezza=%s, vita=%s, fianchi=%s, bmi=%s, trigliceridi=%s, colesterolo_DHL=%s, glucosio=%s, pressione_sistole=%s, pressione_diastole=%s, data_misurazione=%s, menopausa=%s, massa_magra=%s, massa_grassa=%s, idratazione=%s' % (
        self.id_misurazione, 
        self.peso, 
        self.altezza, 
        self.vita, 
        self.fianchi,
        self.bmi, 
        self.trigliceridi,
        self.colesterolo_DHL, 
        self.glucosio, 
        self.pressione_sistole,
        self.pressione_diastole,
        self.data_misurazione, 
        self.menopausa,
        self.massa_magra,
        self.massa_grassa,
        self.idratazione)

    def __json__(self):
        return { 'id_misurazione': self.id_misurazione, 
        'peso': self.peso, 
        'altezza': self.altezza, 
        'vita': self.vita, 
        'fianchi': self.fianchi,
        'bmi': self.bmi, 
        'trigliceridi': self.trigliceridi, 
        'colesterolo_DHL': self.colesterolo_DHL, 
        'glucosio': self.glucosio, 
        'pressione_sistole': self.pressione_sistole,
        'pressione_diastole': self.pressione_diastole,
        'data_misurazione': self.data_misurazione, 
        'menopausa': self.menopausa, 
        'massa_magra': self.massa_magra, 
        'massa_grassa': self.massa_grassa, 
        'idratazione': self.idratazione }
