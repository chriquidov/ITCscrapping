"""
Create Database if it doesn't exist and update the database with the information from scrapping
"""
from sqlalchemy.exc import SQLAlchemyError
import sqlalchemy
from sqlalchemy import BigInteger, String, MetaData, Column, String, Integer, Float, Text, ForeignKey, create_engine
from sqlalchemy_utils import database_exists, create_database
from sqlalchemy.sql import text, func
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy.ext.declarative import declarative_base
import datetime
import pandas as pd
import pymysql
from db_parameter import db_parameter
import sys
import cryptography


def update_mysql_db(job_list, company_list):
    """
    Create Database if it doesn't exist and update the database with the information from job_list and company_list
    :param job_list: list of dictionaries with job attributes
    :param company_list: list of dictionaries with company attributes
    :return:
    """

    # gives default value if the credential is absent
    db_user = db_parameter.get('DATABASE_USER', 'root')
    db_password = db_parameter.get('DATABASE_PASSWORD', 'pass')
    db_port = db_parameter.get('DATABASE_PORT', 3306)
    db_host = db_parameter.get('DATABASE_HOST', "localhost")
    db_name = db_parameter.get('DATABASE_NAME', "indeed_db")

    connection_address_db = f"mysql+pymysql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"
    try:
        engine = create_engine(connection_address_db, echo=True)  # connect to server
    except sqlalchemy.exc.OperationalError as e:
        print(f"Please update the db_parameter.py with correct database parameters and relaunch the program. Error:{e}")
        sys.exit(1)

    # Create the database if it doesn't exist.
    try:
        if not database_exists(engine.url):
            create_database(engine.url)
            engine.connect()
    # Connect the database if exists.
        else:
            engine.connect()
    except sqlalchemy.exc.OperationalError as e:
        print(f"Please update the db_parameter.py with correct database parameters and relaunch the program. Error:{e}")
        sys.exit(1)

    # ORM (object relational mapping)
    # 1. Declaration mapping
    base = declarative_base()
    db_session = sessionmaker(bind=engine)
    session = db_session()

    # The classes are equivalent to tables created in sql
    class Company(base):
        __tablename__ = "Company"

        id = Column(Integer, nullable=False, primary_key=True)
        name = Column(String(200), nullable=False)
        indeed_company_link = Column(String(255))
        rating = Column(Float(2))
        reviews_number = Column(Integer)
        salaries_number = Column(Integer)
        jobs_number = Column(Integer)
        qna_number = Column(Integer)
        photos_number = Column(Integer)
        work_happiness_score = Column(Integer)
        ceo = Column(String(200))
        approved_percentage = Column(Integer)
        founded_year = Column(Integer)
        size = Column(Integer)
        revenue = Column(BigInteger)
        industry = Column(String(200))
        company_link = Column(String(255))

        # Tell ORM to associate Company class with Job class
        Job = relationship("Job", back_populates="Company")

        def __repr__(self):
            return "<Company(id='%s', name='%s', indeed_company_link='%s',rating='%s',reviews_number='%s'" \
                   ",salaries_number='%s',jobs_number='%s',qna_number='%s',photos_number='%s'" \
                   ",work_happiness_score='%s',ceo='%s',approved_percentage='%s',founded_year='%s',size='%s'" \
                   ",revenue='%s',industry='%s',company_link='%s')>" % (
                       self.id, self.name, self.indeed_company_link, self.rating, self.reviews_number,
                       self.salaries_number,
                       self.jobs_number, self.qna_number, self.photos_number,
                       self.work_happiness_score,
                       self.ceo, self.approved_percentage, self.founded_year, self.size, self.revenue, self.industry,
                       self.company_link)

    class Job(base):
        __tablename__ = "Job"

        id = Column(Integer, nullable=False, primary_key=True)
        searched_title = Column(String(100), nullable=False)
        title = Column(String(200), nullable=False)
        summary = Column(Text)
        indeed_company_link = Column(String(255))
        company_name = Column(String(200))
        # Create foreign key to Company.id
        company_id = Column(Integer, ForeignKey("Company.id"))

        # Tell ORM to associate Job class with Company class
        Company = relationship("Company", back_populates="Job")
        Condition = relationship("Condition", back_populates="Job")

        def __repr__(self):
            return "<Job(id='%s', title='%s', summary='%s',indeed_company_link='%s',company_id='%s')>" % (
                self.id, self.title, self.summary, self.indeed_company_link, self.company_id)

    class Condition(base):
        __tablename__ = "Condition"

        id = Column(Integer, nullable=False, primary_key=True)
        job_type = Column(String(200))
        salary = Column(Integer)
        location = Column(String(200))
        # Create foreign key to Job.id
        job_id = Column(Integer, ForeignKey("Job.id"))

        # Tell ORM to associate Condition class with Job class
        Job = relationship("Job", back_populates="Condition")

        def __repr__(self):
            return "<condition(id='%s', job_type='%s', salary='%s',location='%s',job_id='%s')>" % (
                self.id, self.job_type, self.salary, self.location, self.job_id)

    # 2. Create Tables

    # Base.metadata.create_all will find all subclasses of BaseModel, and create these tables in the database,
    # which is equivalent to 'create table'
    base.metadata.create_all(engine)

    # 3. Inserting Data

    # 3.1 Defining Classes to avoid entering duplicate entries
    from sqlalchemy.orm.exc import NoResultFound
    # ...
    num_duplicates_job = 0
    num_added_company = 0
    num_duplicates_company = 0
    num_added_job = 0
    num_updated_company = 0

    def get_update_or_create_company(model, **kwargs):
        """
        Usage:
        class Employee(Base):
            __tablename__ = 'employee'
            id = Column(Integer, primary_key=True)
            name = Column(String, unique=True)

        get_update_or_create_company(Employee, name='bob')
        """
        indeed_company_link_i = list(kwargs.values())[1]
        instance_unique_link_id = get_instance(model.id, indeed_company_link=list(kwargs.values())[1])
        instance_unique_link = get_instance(model, indeed_company_link=list(kwargs.values())[1])
        instance = get_instance(model, **kwargs)

        # if no company detail are provided(no indeed_company_link_i -> skip
        if not indeed_company_link_i:
            data_in_db = 1
            return instance, data_in_db

        # if instance of the unique link(company_indeed_link) doesn't exist -> create new entry
        elif instance_unique_link_id is None:
            instance = create_instance(model, **kwargs)
            data_in_db = 0

        else:
            # if the full instance of the company has at least one different parameter -> update existing entry
            instance_unique_link_id = get_instance(model.id, indeed_company_link=list(kwargs.values())[1])[0]
            if instance is None:
                session.query(model).filter(model.id == instance_unique_link_id).update(kwargs)
                data_in_db = 2
                print(f"{instance_unique_link} updated")
            # if the full instance is exactly the same -> skip
            else:
                data_in_db = 1

        return instance, data_in_db

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
            # mtext = 'model:{}, args:{} => msg:{}'
            # log.error(mtext.format(model, kwargs, msg))## todo when log in place
            session.rollback()
            raise msg
        return instance

    def get_instance(model, **kwargs):
        """Return first instance found."""
        try:
            return session.query(model).filter_by(**kwargs).first()
        except NoResultFound:
            return

    # 3.2 Inserting Companies

    # Initiate a Company instance with no detail (id=1) in case a job has no detail link to
    # the company in Indeed website, in case this item is already present in the database, skip
    try:
        session.query(Company.id).filter_by(id=1).first()[0]
    except TypeError:
        company = Company(id=1, name="No Company detail")
        session.add(company)

    # Populate the new companies only, according to scrapped company dictionary
    for c_dict in company_list:
        company, data_in_db = get_update_or_create_company(model=Company,
                                                           name=c_dict.get("name"),
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
                                                           industry=c_dict.get("Industry"),
                                                           company_link=c_dict.get("Link"))

        # indeed_company_links_dic[c_dict["indeed_company_link"]] = company.id  ###todo remove
        # session.add(company)
        if data_in_db == 1:
            num_duplicates_company += 1
        elif data_in_db == 0:
            num_added_company += 1
        elif data_in_db == 2:
            num_updated_company += 1

    session.commit()

    # 3.3 Inserting Jobs and Conditions
    for j_dict in job_list:
        try:
            comp_id = \
                session.query(Company.id).filter_by(indeed_company_link=j_dict.get("indeed_company_link")).first()[0]
        except TypeError:
            comp_id = 1

        job, data_in_db = get_or_create(model=Job,
                                        company_id=comp_id,
                                        searched_title=j_dict.get("searched_title"),
                                        title=j_dict.get("title"),
                                        summary=j_dict.get("summary"),
                                        company_name=j_dict.get("company"),
                                        indeed_company_link=j_dict.get("indeed_company_link"))

        if data_in_db == 0:
            # Condition
            condition = Condition(Job=job,
                                  job_type=j_dict.get("job_type"),
                                  salary=j_dict.get("salary"),
                                  location=j_dict.get("location"))
            session.add(condition)
            num_added_job += 1
        else:
            num_duplicates_job += 1

    session.commit()
    session.close()
    print("Database Successfully Updated")
    print(f"{num_added_job} new jobs were added to the database")
    print(f"{num_duplicates_job} jobs duplicates found. Those were not added to the database")
    print(f"{num_added_company} new companies were added to the database")

