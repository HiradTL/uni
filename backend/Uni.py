import re
from fastapi import FastAPI, HTTPException, Depends, Query, APIRouter
from pydantic import validator
from fastapi.middleware.cors import CORSMiddleware
from sqlmodel import SQLModel, Field, Session, create_engine, select
from typing import Optional, Annotated
from sqlalchemy.orm import Session as SessionType
from sqlalchemy import BigInteger
from datetime import date
from fastapi.openapi.utils import get_openapi
import jdatetime

sqlite_file_name = "Final.db"
sqlite_url = f"sqlite:///{sqlite_file_name}"

router = APIRouter(prefix="/api")

connect_args = {"check_same_thread": False}
engine = create_engine(sqlite_url, connect_args=connect_args)

# Professors


class Professor(SQLModel, table=True):
    lid: Optional[str] = Field(default=None, primary_key=True)
    fname: str
    lname: str
    nation_id: str = Field(index=True, unique=True)
    department: str
    major: str
    birth_date: str
    born_city: str
    address: str
    postal_code: str
    cphone: str
    hphone: str
    course_ids: str

    class Config:
        validate_assignment = True
        extra = "forbid"
        strict = True

    @validator('lid')
    def validate_lid(cls, num: str):
        if len(num) != 6:
            raise ValueError("کد استاد باید شش رقمی باشد")
        elif not num.isdigit():
            raise ValueError("کد استادی متشکل از اعداد است")
        return num

    @validator("fname", pre=True)
    def validate_professor_fname(cls, fname):
        if len(fname) > 10:
            raise ValueError("حداکثر طول نام باید 10 باشد")
        if not isinstance(fname, str) or not re.match(r'^[\u0600-\u06FF\s]+$', fname):
            raise ValueError("نام باید فقط حاوی کاراکترهای فارسی باشد")
        return fname

    @validator("lname", pre=True)
    def validate_professor_lname(cls, lname):
        if len(lname) > 10:
            raise ValueError("حداکثر طول نام خانوادگی باید 10 باشد")
        if not isinstance(lname, str) or not re.match(r'^[\u0600-\u06FF\s]+$', lname):
            raise ValueError(
                "نام خانوادگی باید فقط حاوی کاراکترهای فارسی باشد")
        return lname

    @validator("department", pre=True)
    def validate_department(cls, department):
        departments = ["فنی مهندسی", "علوم پایه", "اقتصاد"]
        if not isinstance(department, str) or department not in departments:
            raise ValueError(
                "دانشکده باید یکی از دانشکده های مجاز یعنی فنی مهندسی، علوم پایه یا اقتصاد باشد")
        return department

    @validator("major", pre=True)
    def validate_major(cls, major):
        majors = ["مهندسی کامپیوتر", "مهندسی برق", "مهندسی مکانیک",
                  "مهندسی معدن", "مهندسی عمران", "مهندسی شهرسازی", "مهندسی پلیمر"]
        if not isinstance(major, str) or major not in majors:
            raise ValueError(
                "رشته تحصیلی باید یکی از رشته های مجاز دانشکده باشد")
        return major

    @validator("address", pre=True)
    def validate_addres(cls, address):
        if not isinstance(address, str) and len(address) > 100:
            raise ValueError("آدرس باید کمتر از 100 حرف باشد")
        if len(address) < 1:
            raise ValueError("آدرس نمیتواند خالی باشد")
        return address

    @validator('postal_code')
    def validate_postal_code(cls, postal_code: str):
        if len(postal_code) != 10:
            raise ValueError("کد پستی باید ده رقمی باشد")
        elif not postal_code.isdigit():
            raise ValueError("کد پستی متشکل از اعداد است")
        return postal_code

    @validator("born_city")
    def validate_born_city(cls, born_city: str):
        vcities = [
            "تهران", "مشهد", "اصفهان", "کرج", "شیراز", "تبریز", "قم", "اهواز", "کرمانشاه",
            "ارومیه", "رشت", "زاهدان", "همدان", "کرمان", "یزد", "اردبیل", "بندرعباس",
            "اراک", "اسلامشهر", "زنجان", "سنندج", "قزوین", "خرم‌آباد", "گرگان",
            "ساری", "بجنورد", "بوشهر", "بیرجند", "ایلام", "شهرکرد", "یاسوج"
        ]
        if not isinstance(born_city, str) or born_city not in vcities:
            raise ValueError(
                "محل تولد باید یکی از مراکز استان ها در کشور باشد")
        return born_city

    @validator("cphone")
    def validate_cell_phone(cls, phone_number):
        if not phone_number.isdigit():
            raise ValueError("کد استادی متشکل از اعداد است")
        if len(phone_number) != 11:
            raise ValueError("شماره تلقن همراه یاید 11 زقم باشد")
        if not phone_number.startswith("09"):
            raise ValueError("شماره تلقن همراه باید با 09 شروغ شود")
        return phone_number

    @validator("hphone")
    def validate_home_phone(cls, phone_number):
        if len(phone_number) != 11:
            raise ValueError("شماره تلفن ثابت باید 11 رقم باشد")
        vhphone = ["021", "031", "041", "042", "045", "051", "052", "053", "054", "055", "056", "057", "058", "059", "061", "062", "063", "064", "065", "066", "067", "068", "069", "070", "071", "072",
                   "073", "074", "075", "076", "077", "078", "079", "080", "081", "082", "083", "084", "085", "086", "087", "088", "089", "090", "091", "092", "093", "094", "095", "096", "097", "098", "099"]
        if phone_number[:3] not in vhphone:
            raise ValueError("پیش شماره تلفن ثابت نادرست است")
        return phone_number

    @validator("birth_date", pre=True)
    def validate_birth_date(cls, date):
        parts = date.split("/")
        if len(parts) != 3:
            raise ValueError("فرمت تاریخ باید به صورت YYYY/MM/DD باشد")

        try:
            day, month, year = map(int, parts)
        except ValueError:
            raise ValueError(
                "تاریخ باید فقط شامل اعداد صحیح باشد (مثلاً ۱۳۷۵/۰۵/۲۳)")

        if not (1300 <= year <= 1400):
            raise ValueError("سال باید بین ۱۳۰۰ تا ۱۴۰۰ باشد")

        if not (1 <= month <= 12):
            raise ValueError("ماه باید بین ۱ تا ۱۲ باشد")

        if not (1 <= day <= 31):
            raise ValueError("روز باید بین ۱ تا ۳۱ باشد")
        if month in [1, 2, 3, 4, 5, 6] and day > 31:
            raise ValueError(f"ماه {month} حداکثر ۳۱ روز دارد")
        elif month in [7, 8, 9, 10, 11] and day > 30:
            raise ValueError(f"ماه {month} حداکثر ۳۰ روز دارد")
        elif month == 12 and day > 30:
            raise ValueError(
                "اسفندماه حداکثر ۳۰ روز دارد (بدون در نظر گرفتن سال کبیسه)")
        return date

    @validator("nation_id")
    def validate_nation_id(cls, nid):
        if not nid.isdigit():
            raise ValueError("کد ملی تنها باید از ارقام تشکیل شده باشد.")
        if len(nid) != 10:
            raise ValueError("کد ملی باید عددی ده‌رقمی باشد.")
        if len(set(nid)) == 1:
            raise ValueError(
                "کد ملی نمی‌تواند از ارقام تکراری تشکیل شده باشد.")
        check = int(nid[9])
        s = sum(int(nid[i]) * (10 - i) for i in range(9)) % 11
        if (s < 2 and check != s) or (s >= 2 and check != (11 - s)):
            raise ValueError("کد ملی وارد شده نامعتبر است.")
        return nid


# Students
class Student(SQLModel, table=True):
    stid: Optional[str] = Field(default=None, primary_key=True)
    fname: str
    lname: str
    father: str
    birth: str
    ids_number: str = Field(max_length=6, min_length=6)
    ids_letter: str = Field(max_length=1)
    ids_code: str = Field(max_length=2, min_length=2)
    borncity: str
    address: str
    postalcode: str
    cphone: str
    hphone: str
    department: str
    married: str
    nid: str
    major: str
    courseids: str
    lids: str

    class Config:
        validate_assignment = True
        extra = "forbid"
        strict = True

    @validator("stid", pre=True)
    def validate_stid(cls, stid_value):
        if not isinstance(stid_value, str):
            raise ValueError("کد دانشجویی را در قالب یک رشته وارد کنید")
        if not stid_value.isdigit():
            raise ValueError("شماره دانشجویی باید تنها متشکل از اعداد باشد")
        if not (stid_value.startswith("403114150")):
            raise ValueError(
                "قالب شماره دانشجویی صحیح نیست ( شماره دانشجویی باید با 403114150 شروع بشود)")
        if len(stid_value) != 11:
            raise ValueError("شماره دانشجویی باید دارای 11 رقم باشد")
        return stid_value

    @validator("fname", pre=True)
    def validate_fname(cls, fname):
        if not isinstance(fname, str) or not re.match(r'^[\u0600-\u06FF\s]+$', fname):
            raise ValueError("نام باید تنها متشکل از حروف فارسی باشد")
        return fname

    @validator("lname", pre=True)
    def validate_lname(cls, lname):
        if not isinstance(lname, str) or not re.match(r'^[\u0600-\u06FF\s]+$', lname):
            raise ValueError("نام خانوادگی باید تنها متشکل از حروف فارسی باشد")
        return lname

    @validator("father", pre=True)
    def validate_father(cls, father):
        if not isinstance(father, str) or not re.match(r'^[\u0600-\u06FF\s]+$', father):
            raise ValueError("نام پدر باید تنها متشکل از حروف فارسی باشد")
        return father

    @validator("ids_number", pre=True)
    def validate_ids_number(cls, ids_number):
        if not isinstance(ids_number, str) or not (ids_number.isdigit() and len(ids_number) == 6):
            raise ValueError("سریال شناسنامه باید عدد ۶ رقمی باشد")
        return ids_number

    @validator("ids_letter", pre=True)
    def validate_ids_letter(cls, ids_letter):
        persian_letters = "آابپتثجچحخدذرزژسشصضطظعغفقکگلمنوهی"
        if not isinstance(ids_letter, str) or ids_letter not in persian_letters:
            raise ValueError("حرف سریال شناسنامه باید یکی از حروف فارسی باشد")
        return ids_letter

    @validator("ids_code", pre=True)
    def validate_ids_code(cls, ids_code):
        if not isinstance(ids_code, str) or not (ids_code.isdigit() and len(ids_code) == 2):
            raise ValueError("کد سریال شناسنامه باید عدد ۲ رقمی باشد")
        return ids_code

    @validator("borncity", pre=True)
    def validate_borncity(cls, borncity):
        valid_cities = [
            "تهران", "مشهد", "اصفهان", "کرج", "شیراز", "تبریز", "قم", "اهواز", "کرمانشاه",
            "ارومیه", "رشت", "زاهدان", "همدان", "کرمان", "یزد", "اردبیل", "بندرعباس",
            "اراک", "اسلامشهر", "زنجان", "سنندج", "قزوین", "خرم‌آباد", "گرگان",
            "ساری", "بجنورد", "بوشهر", "بیرجند", "ایلام", "شهرکرد", "یاسوج"
        ]
        if borncity not in valid_cities:
            raise ValueError("شهر محل تولد باید یکی از مراکز استان ها باشد")
        return borncity

    @validator("birth", pre=True)
    def validate_birth(cls, date):
        parts = date.split("/")
        if len(parts) != 3:
            raise ValueError("فرمت تاریخ باید به صورت YYYY/MM/DD باشد")

        try:
            day, month, year = map(int, parts)
        except ValueError:
            raise ValueError(
                "تاریخ باید فقط شامل اعداد صحیح باشد (مثلاً ۱۳۷۵/۰۵/۲۳)")

        if not (1300 <= year <= 1400):
            raise ValueError("سال باید بین ۱۳۰۰ تا ۱۴۰۰ باشد")

        if not (1 <= month <= 12):
            raise ValueError("ماه باید بین ۱ تا ۱۲ باشد")

        if not (1 <= day <= 31):
            raise ValueError("روز باید بین ۱ تا ۳۱ باشد")
        if month in [1, 2, 3, 4, 5, 6] and day > 31:
            raise ValueError(f"ماه {month} حداکثر ۳۱ روز دارد")
        elif month in [7, 8, 9, 10, 11] and day > 30:
            raise ValueError(f"ماه {month} حداکثر ۳۰ روز دارد")
        elif month == 12 and day > 30:
            raise ValueError(
                "اسفندماه حداکثر ۳۰ روز دارد (بدون در نظر گرفتن سال کبیسه)")
        return date

    @validator("address", pre=True)
    def validate_address(cls, address):
        if not isinstance(address, str) or len(address) > 100:
            raise ValueError("آدرس باید حداکثر دارای ۱۰۰ حرف باشد")
        if len(address) < 1:
            raise ValueError("آدرس نمیتواند خالی باشد")
        return address

    @validator("postalcode", pre=True)
    def validate_postalcode(cls, postalcode):
        if not isinstance(postalcode, str) or not (postalcode.isdigit() and len(postalcode) == 10):
            raise ValueError("کد پستی باید عدد ۱۰ رقمی باشد")
        return postalcode

    @validator("cphone")
    def validate_cell_phone(cls, phone_number):
        if not phone_number.isdigit():
            raise ValueError("شماره تلفن همراه باید تنها متشکل از اعداد باشد")
        if len(phone_number) != 11:
            raise ValueError("شماره تلفن همراه باید دارای 11 رقم باشد")
        if not phone_number.startswith("09"):
            raise ValueError("شماره تلفن همراه باید با 09 شروغ شود")
        return phone_number

    @validator("hphone")
    def validate_hphone(cls, hphone):
        vhphone = ["021", "031", "041", "042", "045", "051", "052", "053", "054", "055", "056", "057", "058", "059", "061", "062", "063", "064", "065", "066", "067", "068", "069", "070", "071", "072",
                   "073", "074", "075", "076", "077", "078", "079", "080", "081", "082", "083", "084", "085", "086", "087", "088", "089", "090", "091", "092", "093", "094", "095", "096", "097", "098", "099"]
        if hphone[:3] not in vhphone:
            raise ValueError("پیش شماره تلفن ثابت نادرست است")
        if len(hphone) != 11:
            raise ValueError("شماره تلفن ثابت باید 11 رقم باشد")
        return hphone

    @validator("department", pre=True)
    def validate_department(cls, department):
        departments = ["فنی مهندسی", "علوم پایه", "اقتصاد"]
        if department not in departments:
            raise ValueError(
                "دانشکده باید یکی از دانشکده های {فنی مهندسی، علوم پایه یا اقتصاد} باشد")
        return department

    @validator("major", pre=True)
    def validate_major(cls, major):
        majors = {
            "فنی مهندسی": ["مهندسی کامپیوتر", "مهندسی برق", "مهندسی مکانیک"],
            "علوم پایه": ["ریاضی", "فیزیک", "شیمی"],
            "اقتصاد": ["اقتصاد", "مدیریت", "حسابداری"]
        }
        for major_list in majors.values():
            if major in major_list:
                return major
        raise ValueError("رشته تحصیلی باید معتبر و مرتبط با دانشکده باشد")

    @validator("married", pre=True)
    def validate_married(cls, married):
        if married not in ["مجرد", "متاهل"]:
            raise ValueError("وضعیت تأهل باید {مجرد یا متاهل} باشد")
        return married

    @validator("nid")
    def validate_nid(cls, nid):
        if not nid.isdigit():
            raise ValueError("کد ملی تنها باید از ارقام تشکیل شده باشد.")
        if len(nid) != 10:
            raise ValueError("کد ملی باید عددی ده‌رقمی باشد.")
        if len(set(nid)) == 1:
            raise ValueError(
                "کد ملی نمی‌تواند از ارقام تکراری تشکیل شده باشد.")

        check = int(nid[9])
        s = sum(int(nid[i]) * (10 - i) for i in range(9)) % 11
        if (s < 2 and check != s) or (s >= 2 and check != (11 - s)):
            raise ValueError("کد ملی وارد شده نامعتبر است.")
        return nid


# Courses
class Course(SQLModel, table=True):
    cid: Optional[str] = Field(default=None, primary_key=True)
    course_name: str
    credit: int
    department: str

    class Config:
        validate_assignment = True
        extra = "forbid"
        strict = True

    @validator('cid')
    def validate_cid(cls, cid):
        if len(cid) != 5:
            raise ValueError("کد درس باید پنج رقمی باشد")
        elif not cid.isdigit():
            raise ValueError("کد درس تنها متشکل از اعداد است")
        return cid

    @validator('course_name')
    def validate_course_name(cls, course_name):
        if len(course_name) > 25:
            raise ValueError("حداکثر طول نام درس باید 25 حرف باشد")
        if not isinstance(course_name, str) or not re.match(r'^[\u0600-\u06FF\s]+$', course_name):
            raise ValueError("نام درس تنها باید حاوی حروف فارسی باشد")
        return course_name

    @validator('credit')
    def validate_credit(cls, credit):
        if credit > 4 or credit < 1:
            raise ValueError("تعداد واحد عددی صحیح از بازه 1 تا 4 است")
        return credit

    @validator('department')
    def validate_department(cls, department):
        departments = ["فنی مهندسی", "علوم پایه", "اقتصاد"]
        if not isinstance(department, str) or department not in departments:
            raise ValueError(
                "دانشکده باید یکی از دانشکده های مجاز یعنی فنی مهندسی، علوم پایه یا اقتصاد باشد")
        return department

# ایجاد جدول‌ها


def create_db_and_tables():
    SQLModel.metadata.create_all(engine)

# ایجاد Session برای ارتباط با پایگاه داده


def get_session():
    with Session(engine) as session:
        yield session


SessionDep = Annotated[Session, Depends(get_session)]

# ایجاد جدول‌ها هنگام شروع برنامه


@router.on_event("startup")
def on_startup():
    create_db_and_tables()


@router.post("/professors/")
def create_professor(professor: Professor):
    with Session(engine) as session:
        existing_professor = session.exec(
            select(Professor).where(Professor.nation_id == professor.nation_id)
        ).first()
        if existing_professor:
            raise HTTPException(
                status_code=400, detail="کد ملی قبلاً ثبت شده است.")

        session.add(professor)
        session.commit()
        session.refresh(professor)
    return professor


@router.get("/professors/{professor_id}")
def read_professor(professor_id: str):
    with Session(engine) as session:
        professor = session.get(Professor, professor_id)
    if professor is None:
        return {"message": "Professor not found"}
    return professor


@router.get("/professors/")
def read_professors(
    session: SessionDep,
    offset: int = 0,
    limit: Annotated[int, Query(le=100)] = 100,
) -> list[Professor]:
    professors = session.exec(
        select(Professor).offset(offset).limit(limit)).all()
    return professors


@router.post("/students/")
def create_student(student: Student):
    with Session(engine) as session:
        session.add(student)
        session.commit()
        session.refresh(student)
    return student


@router.get("/students/{student_id}")
def read_student(student_id: str):
    with Session(engine) as session:
        student = session.get(Student, student_id)
    if student is None:
        return {"message": "Student not found"}
    return student


@router.get("/students/")
def read_students(
    session: SessionDep,
    offset: int = 0,
    limit: Annotated[int, Query(le=100)] = 100,
) -> list[Student]:
    students = session.exec(select(Student).offset(offset).limit(limit)).all()
    return students


@router.post("/courses/")
def create_course(course: Course):
    with Session(engine) as session:
        session.add(course)
        session.commit()
        session.refresh(course)
    return course


@router.get("/courses/{course_id}")
def read_course(course_id: str):
    with Session(engine) as session:
        course = session.get(Course, course_id)
    if course is None:
        return {"message": "Course not found"}
    return course


@router.get("/courses/")
def read_courses(
    session: SessionDep,
    offset: int = 0,
    limit: Annotated[int, Query(le=100)] = 100,
) -> list[Course]:
    courses = session.exec(select(Course).offset(offset).limit(limit)).all()
    return courses


@router.delete("/professors/{professor_id}")
def delete_professor(professor_id: str):
    with Session(engine) as session:
        professor = session.get(Professor, professor_id)
        if professor:
            session.delete(professor)
            session.commit()
            return {"message": "Professor deleted"}
        else:
            return {"message": "Professor not found"}


@router.delete("/students/{student_id}")
def delete_student(student_id: str):
    with Session(engine) as session:
        student = session.get(Student, student_id)
        if student:
            session.delete(student)
            session.commit()
            return {"message": "Student deleted"}
        else:
            return {"message": "Student not found"}


@router.delete("/courses/{course_id}")
def delete_course(course_id: str):
    with Session(engine) as session:
        course = session.get(Course, course_id)
        if course:
            session.delete(course)
            session.commit()
            return {"message": "Course deleted"}
        else:
            return {"message": "Course not found"}


def get_session_dep():
    with Session(engine) as session:
        yield session


@router.put("/professors/{professor_id}")
def update_professor(professor_id: str, professor: Professor, session: SessionType = Depends(get_session_dep)) -> Professor:
    db_professor = session.get(Professor, professor_id)
    if not db_professor:
        raise HTTPException(status_code=404, detail="Professor not found")
    prof_data = professor.dict(exclude_unset=True)
    for key, value in prof_data.items():
        setattr(db_professor, key, value)
    session.add(db_professor)
    session.commit()
    session.refresh(db_professor)
    return db_professor


@router.put("/students/{student_id}")
def update_student(student_id: str, student: Student, session: SessionType = Depends(get_session_dep)) -> Student:
    db_student = session.get(Student, student_id)
    if not db_student:
        raise HTTPException(status_code=404, detail="Student not found")
    student_data = student.dict(exclude_unset=True)
    for key, value in student_data.items():
        setattr(db_student, key, value)
    session.add(db_student)
    session.commit()
    session.refresh(db_student)
    return db_student


@router.put("/courses/{course_id}")
def update_course(course_id: str, course: Course, session: SessionType = Depends(get_session_dep)) -> Course:
    db_course = session.get(Course, course_id)
    if not db_course:
        raise HTTPException(status_code=404, detail="Course not found")
    course_data = course.dict(exclude_unset=True)
    for key, value in course_data.items():
        setattr(db_course, key, value)
    session.add(db_course)
    session.commit()
    session.refresh(db_course)
    return db_course


app = FastAPI(
    title="University API",
    version="1.0.0",
    description="API for managing students, professors, and courses.",
    openapi_url="/api/openapi.json",
    docs_url="/api/docs",
    redoc_url="/api/redoc"
)
origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    openapi_schema = get_openapi(
        title="University System API",
        version="1.0.0",
        description="API Documentation",
        routes=app.routes,
    )
    app.openapi_schema = openapi_schema
    return app.openapi_schema


app.openapi = custom_openapi

app.include_router(router)
