"""
Create Database if doesn't exist and update the database with the information from scrapping
"""
from sqlalchemy.exc import SQLAlchemyError
import sqlalchemy
from sqlalchemy import Table, Column, Integer, String, MetaData, Column, String, Integer, Float, TIMESTAMP, Text, \
    NVARCHAR, VARCHAR, ForeignKey, create_engine
from sqlalchemy_utils import database_exists, create_database
from sqlalchemy.sql import text, func
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy.ext.declarative import declarative_base
# from flask import Flask
# from flask_sqlalchemy import SQLAlchemy
import datetime
import pandas as pd
import pymysql
from db_parameter import db_parameter
import cryptography


def update_mysql_db(job_list, company_list):
    """
    Create Database if doesn't exist and update the database with the information from job_list and company_list
    :param job_list: list of dictionaries with job attributes
    :param company_list: list of dictionaries with company attributes
    :return:
    """
    # app = Flask(__name__)
    # app.config["DEBUG"] = True

    # gives default value if the credential is absent
    db_user = db_parameter.get('DATABASE_USER', 'root')
    db_password = db_parameter.get('DATABASE_PASSWORD', 'pass')
    db_port = db_parameter.get('DATABASE_PORT', 3306)
    db_host = db_parameter.get('DATABASE_HOST', "localhost")
    db_name = db_parameter.get('DATABASE_NAME', "indeed_db")

    connection_address_db = f"mysql+pymysql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"
    engine = create_engine(connection_address_db, echo=True)  # connect to server

    # Todo exception bad db parameter -> Please edit the db_parameter file

    # Create the database if it doesn't exist.
    if not database_exists(engine.url):
        create_database(engine.url)
        engine.connect()
    # Connect the database if exists.
    else:
        engine.connect()

    # app.config['SQLALCHEMY_DATABASE_URI'] = connection_address_db
    # db = SQLAlchemy(app)

    # ORM (object relational mapping)
    # 1. Declaration mapping
    base = declarative_base()
    db_session = sessionmaker(bind=engine)
    session = db_session()
    indeed_company_links_dic = {}

    # The classes are equivalent to tables created in sql
    class Company(base):
        __tablename__ = "Company"

        # id = Column(Integer, nullable=False, primary_key=True)
        # name = Column(String(100), nullable=False)
        # indeed_company_link = Column(VARCHAR(2048))
        # rating = Column(Float)
        # reviews_number = Column(Integer)
        # salaries_number = Column(Integer)
        # jobs_number = Column(Integer)
        # qna_number = Column(Integer)
        # interviews_number = Column(Integer)
        # photos_number = Column(Integer)
        # work_happiness_score = Column(Integer)
        # ceo = Column(String(100))
        # approved_percentage = Column(Integer)
        # founded_year = Column(Integer)
        # size = Column(Integer)
        # revenue = Column(Integer)
        # industry = Column(String(200))
        # company_link = Column(VARCHAR(2048))
        #
        id = Column(Integer, nullable=False, primary_key=True)
        name = Column(String(100), nullable=False)
        indeed_company_link = Column(String(200))
        rating = Column(String(200))
        reviews_number = Column(String(200))
        salaries_number = Column(String(200))
        jobs_number = Column(String(200))
        qna_number = Column(String(200))
        photos_number = Column(String(200))
        work_happiness_score = Column(String(200))
        ceo = Column(String(200))
        approved_percentage = Column(String(200))
        founded_year = Column(String(200))
        size = Column(String(200))
        revenue = Column(String(200))
        industry = Column(String(200))
        company_link = Column(VARCHAR(2048))

        # Tell ORM to associate Company class with Job class
        Job = relationship("Job", back_populates="Company")

        def __repr__(self):
            return "<Company(id='%s', name='%s', indeed_company_link='%s',rating='%s',reviews_number='%s'" \
                   ",salaries_number='%s',jobs_number='%s',qna_number='%s',photos_number='%s'" \
                   ",work_happiness_score='%s',ceo='%s',approved_percentage='%s',founded_year='%s',size='%s'" \
                   ",revenue='%s',industry='%s',company_link='%s')>" % (
                       self.id, self.name, self.indeed_company_link, self.rating, self.reviews_number,
                       self.salaries_number,
                       self.jobs_number, self.qna_number,  self.photos_number,
                       self.work_happiness_score,
                       self.ceo, self.approved_percentage, self.founded_year, self.size, self.revenue, self.industry,
                       self.company_link)

    class Job(base):
        __tablename__ = "Job"

        id = Column(Integer, nullable=False, primary_key=True)
        title = Column(String(100), nullable=False)
        summary = Column(VARCHAR(2048))  ##todo check type
        indeed_company_link = Column(VARCHAR(2048))
        # Create foreign key to Company.id
        company_id = Column(Integer, ForeignKey("Company.id"))  ##todo back_populate

        # Tell ORM to associate Job class with Company class
        Company = relationship("Company", back_populates="Job")
        Condition = relationship("Condition", back_populates="Job")

        def __repr__(self):
            return "<Job(id='%s', title='%s', summary='%s',indeed_company_link='%s',company_id='%s')>" % (
                self.id, self.title, self.summary, self.indeed_company_link, self.company_id)

    class Condition(base):
        __tablename__ = "Condition"

        id = Column(Integer, nullable=False, primary_key=True)
        job_type = Column(String(100))
        salary = Column(String(200))
        location = Column(String(100))
        # Create foreign key to Job.id
        job_id = Column(Integer, ForeignKey("Job.id"))  ##todo back_populate

        # Tell ORM to associate Condition class with Job class
        Job = relationship("Job", back_populates="Condition")

        def __repr__(self):
            return "<condition(id='%s', job_type='%s', salary='%s',location='%s',job_id='%s')>" % (
                self.id, self.job_type, self.salary, self.location, self.job_id)

    # 2. Create Tables

    # Base.metadata.create_all will find all subclasses of BaseModel, and create these tables in the database,
    # which is equivalent to 'create table'
    base.metadata.create_all(engine)  # todo check if data exist before inserting

    # 3. Inserting Data

    # 3.1 Defining Classes to avoid entering duplicate entries
    from sqlalchemy.orm.exc import NoResultFound
    # ...
    num_duplicates_job = 0
    num_added_company=0
    num_duplicates_company = 0
    num_added_job=0


    def get_or_create(model, **kwargs):
        """
        Usage:
        class Employee(Base):
            __tablename__ = 'employee'
            id = Column(Integer, primary_key=True)
            name = Column(String, unique=True)

        get_or_create(Employee, name='bob')
        """
        instance = get_instance(model, **kwargs)

        if instance is None:
            instance = create_instance(model, **kwargs)
            data_in_db = 0
        else:
            data_in_db = 1

        return instance, data_in_db

    def create_instance(model, **kwargs):
        """create instance"""
        try:
            instance = model(**kwargs)
            session.add(instance)
            session.flush()
        except Exception as msg:
            mtext = 'model:{}, args:{} => msg:{}'
            # log.error(mtext.format(model, kwargs, msg))
            session.rollback()
            raise (msg)
        return instance

    def get_instance(model, **kwargs):
        """Return first instance found."""
        try:
            return session.query(model).filter_by(**kwargs).first()
        except NoResultFound:
            return

    # 3.2 Inserting Companies
    try:
        comp_1 = session.query(Company.id).filter_by(id=1).first()[0]
    except TypeError:  ### todo check
        company = Company(id=1, name="No Company detail")
        session.add(company)

    for c_dict in company_list:  # todo replace companies_dict
        company, data_in_db = get_or_create(model=Company, name=c_dict.get("name"),
                                        indeed_company_link=c_dict.get("indeed_company_link"),
                                        rating=c_dict.get("rating"),
                                        reviews_number=c_dict.get('reviews-tab'),
                                        salaries_number=c_dict.get('salaries-tab'),
                                        jobs_number=c_dict.get('jobs-tab'),
                                        qna_number=c_dict.get('qna-tab'),
                                        photos_number=c_dict.get('photos-tab'),
                                        work_happiness_score=c_dict.get('Work Happiness Score'),
                                        ceo=c_dict.get("CEO"),
                                        approved_percentage=c_dict.get("Approved"),
                                        founded_year=c_dict.get("Founded"),
                                        size=c_dict.get("Company size"),
                                        revenue=c_dict.get("Revenue"),
                                        industry=c_dict.get("Industry'"),
                                        company_link=c_dict.get("Link"))

        indeed_company_links_dic[c_dict["indeed_company_link"]] = company.id  ### to solve
        # session.add(company)
        if data_in_db == 1:
            num_duplicates_company += 1
        else:
            num_added_company += 1

    session.commit()

    # 3.3 Inserting Jobs and Conditions
    for j_dict in job_list:
        try:
            comp_id = \
                session.query(Company.id).filter_by(indeed_company_link=j_dict.get("indeed_company_link")).first()[0]
        except TypeError:  ### todo check
            comp_id = 1

        job, data_in_db = get_or_create(model=Job, company_id=comp_id,
                                        title=j_dict.get("title"),
                                        summary=j_dict.get("summary"),
                                        indeed_company_link=j_dict.get("indeed_company_link"))

        #
        # job = Job(company_id=comp_id,
        #           title=j_dict.get("title"),
        #           summary=j_dict.get("summary"),
        #           detail_link=j_dict.get("indeed_company_link")
        #           )
        # session.add(job)
        if data_in_db == 0:
            # Condition
            condition = Condition(Job=job,
                                  job_type=j_dict.get("job_type"),
                                  salary=j_dict.get("salary"),
                                  location=j_dict.get("location"))
            session.add(condition)
            num_added_job+= 1
        else:
            num_duplicates_job += 1


    session.commit()
    session.close()
    print("Database Successfully Updated")
    print(f"{num_added_job} new jobs were added to the database")
    print(f"{num_duplicates_job} jobs duplicates found. Those were not added to the database")
    print(f"{num_added_company} new companies were added to the database")
    print(f"{num_duplicates_company} companies duplicates found. Those were not added to the database")