from F_taste_misurazioni.db import Base
from sqlalchemy import Column, Integer, String, LargeBinary
from sqlalchemy.orm import relationship

class NutrizionistaModel(Base):
    __tablename__ = 'nutrizionista'
    
    id_nutrizionista = Column(Integer, primary_key=True)
    nome = Column(String(45), nullable=False)
    cognome = Column(String(45), nullable=False)
    password = Column(LargeBinary, nullable=False)
    email = Column(String(45), unique = True, nullable=False)
    link_informativa = Column(String(50))
    pazienti = relationship("PazienteModel", back_populates='nutrizionista', lazy=True)
    
    def __init__(self, nome, cognome, password, email):
        self.nome = nome
        self.cognome = cognome
        self.password = password
        self.email = email
        self.link_informativa = ""

    def __repr__(self):
        return 'NutrizionistaModel(id_nutrizionista=%s, nome=%s, cognome=%s, password=%s, email=%s, link_informativa=%s' % (self.id_nutrizionista, self.nome, self.cognome, self.password, self.email, self.link_informativa)

    def __json__(self):
        return { 'id_nutrizionista' : self.id_nutrizionista,
                 'nome' : self.nome,
                 'cognome' : self.cognome,
                 'email' : self.email, 
                 'link_informativa' : self.link_informativa if self.link_informativa is not None else None }

        