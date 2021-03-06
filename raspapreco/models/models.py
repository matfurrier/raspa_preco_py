"""DataBase models for raspapreco mod1"""
import os
from collections import OrderedDict

from sqlalchemy import (Column, DateTime, ForeignKey, Integer, LargeBinary,
                        Numeric, PickleType, String, Table, create_engine)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, scoped_session, sessionmaker


class MySession():
    def __init__(self, base, test=False):
        if test:
            path = ':memory:'
        else:
            path = os.path.join(os.path.dirname(
                os.path.abspath(__file__)), 'raspa.db')
            if os.name != 'nt':
                path = '/' + path
        self._engine = create_engine('sqlite:///' + path, convert_unicode=True)
        Session = sessionmaker(bind=self._engine)
        if test:
            self._session = Session()
        else:
            self._session = scoped_session(Session)
            base.metadata.bind = self._engine

    def session(self):
        return self._session

    def engine(self):
        return self._engine


Base = declarative_base()

produto_procedimento = Table('produto_procedimento', Base.metadata,
                             Column('left_id', Integer,
                                    ForeignKey('procedimentos.id')),
                             Column('right_id', Integer,
                                    ForeignKey('produtos.id'))
                             )

site_procedimento = Table('site_procedimento', Base.metadata,
                          Column('left_id', Integer,
                                 ForeignKey('procedimentos.id')),
                          Column('right_id', Integer,
                                 ForeignKey('sites.id'))
                          )


class Procedimento(Base):
    """Guarda os dados do procedimento"""
    __tablename__ = 'procedimentos'
    id = Column(Integer, primary_key=True)
    nome = Column(String(20), unique=True)
    produtos = relationship(
        'Produto',
        secondary=produto_procedimento,
        back_populates='procedimentos')
    sites = relationship(
        'Site',
        secondary=site_procedimento,
        back_populates='procedimentos')
    dossies = relationship('Dossie', back_populates='procedimento')

    def __init__(self, nome):
        self.nome = nome


class Produto(Base):
    """Um produto a pesquisar"""
    __tablename__ = 'produtos'
    id = Column(Integer, primary_key=True)
    descricao = Column(String(50), unique=True)
    preco_declarado = Column(Numeric(asdecimal=False))
    procedimentos = relationship(
        'Procedimento',
        secondary=produto_procedimento,
        back_populates='produtos')
    produtos_encontrados = relationship(
        'ProdutoEncontrado', back_populates='produto')

    def __init__(self, descricao, preco_declarado):
        self.descricao = descricao
        self.preco_declarado = preco_declarado


class Site(Base):
    """Um site que sera fonte de dados"""
    # TODO: Permitir targets dinâmicos com subtabela targets
    # Depois, modificar scrap e ProdutoEncontrado para também
    # permitir comportamento dinâmico. Assim, app será para
    # qqer scrap, não só produto/preço

    __tablename__ = 'sites'
    id = Column(Integer, primary_key=True)
    title = Column(String(20), unique=True)
    url = Column(String(200))
    targets = Column(PickleType)
    procedimentos = relationship(
        'Procedimento',
        secondary=site_procedimento,
        back_populates='sites')
    produtos_encontrados = relationship(
        'ProdutoEncontrado', back_populates='site')

    def __init__(self, title, url):
        self.title = title
        self.url = url


class Dossie(Base):
    """Resulta de um "scrap" de um Procedimento em uma
    data, refinado"""
    __tablename__ = 'dossies'
    id = Column(Integer, primary_key=True)
    data = Column(DateTime)
    # task_id estará preenchido apenas se produtos_econtrados
    # do dossiê estiverem sendo preenchidos em background
    task_id = Column(String(50))
    procedimento_id = Column(Integer, ForeignKey('procedimentos.id'))
    procedimento = relationship('Procedimento', back_populates='dossies')
    produtos_encontrados = relationship(
        'ProdutoEncontrado', back_populates='dossie')

    def __init__(self, procedimento, data):
        self.procedimento_id = procedimento.id
        self.data = data


class ProdutoEncontrado(Base):
    """Informações de produto na página pesquisada
    que pode ser idêntico/similar ao produto desejado"""
    __tablename__ = 'produtosencontrados'
    id = Column(Integer, primary_key=True)
    produto_id = Column(Integer, ForeignKey('produtos.id'))
    produto = relationship(
        'Produto', back_populates='produtos_encontrados')
    site_id = Column(Integer, ForeignKey('sites.id'))
    site = relationship(
        'Site', back_populates='produtos_encontrados')
    dossie_id = Column(Integer, ForeignKey('dossies.id'))
    dossie = relationship(
        'Dossie', back_populates='produtos_encontrados')
    descricao_site = Column(String(200))
    url = Column(String(200))
    preco = Column(Numeric(asdecimal=False))
    foto = Column(LargeBinary)
    campos = Column(PickleType)

    def __init__(self, dossie, produto, site, descricao_site, url, preco):
        self.dossie_id = dossie.id
        self.produto_id = produto.id
        self.site_id = site.id
        self.descricao_site = descricao_site
        self.url = url
        self.preco = preco

    def to_dict(self):
        return OrderedDict({'data': self.dossie.data,
                            'produto': self.produto.descricao,
                            'site': self.site.title,
                            'descricao_site': self.descricao_site,
                            'url': self.url,
                            'preco': self.preco
                            })


if __name__ == '__main__':
    import alembic.config
    alembicArgs = [
        'revision',
        '--autogenerate', '-m "from code"',
    ]
    alembic.config.main(argv=alembicArgs)
    alembicArgs = [
        '--raiseerr',
        'upgrade', 'head',
    ]
    alembic.config.main(argv=alembicArgs)
#    asession = MySession(Base)
#    Base.metadata.drop_all(asession.engine())
#    Base.metadata.create_all(asession.engine())
