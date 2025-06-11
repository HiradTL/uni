import streamlit as st
import requests
import pandas as pd
from typing import Dict, List

BASE_URL = "http://backend:8000/api"


def submit_form(endpoint: str, data: Dict):
    try:
        response = requests.post(
            f"{BASE_URL}/{endpoint}/",
            json=data,
            headers={"Content-Type": "application/json"}
        )
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        st.error(f"خطا در ارسال داده: {str(e)}")
        return None


st.set_page_config(page_title="سیستم مدیریت دانشگاه",
                   page_icon="🎓", layout="centered")

# استایل سفارشی برای تم مشکی و بنفش و سایدبار سمت راست

st.markdown("""
    <style>
        /* چیدمان معکوس برای بدنه و تولبار */
        .reportview-container {
            flex-direction: row-reverse;
        }
        header > .toolbar {
            flex-direction: row-reverse;
            left: 1rem;
            right: auto;
        }

        body {
            background-color: #1a1a1a;
            color: #ffffff;
            font-family: 'Vazir', sans-serif;
            font-size: 18px;
        }
        .stApp {
            background-color: #1a1a1a;
            color: #ffffff;
        }
        h1 {
            font-size: 36px;
            color: #ffffff;
            text-align: center;
        }
        h2, h3 {
            font-size: 24px;
            color: #ffffff;
        }
        .stButton>button {
            background-color: #6a0dad;
            color: #ffffff;
            border-radius: 5px;
            border: 1px solid #ffffff;
            font-size: 16px;
            padding: 8px 16px;
            margin: 5px;
        }
        .stTextInput>div>input, .stSelectbox>div>select, .stNumberInput>div>input, .stTextArea textarea {
            background-color: #2c2c2c;
            color: #ffffff;
            border: 1px solid #6a0dad;
            font-size: 16px;
        }
        .stAlert {
            background-color: #3c2f4f;
            color: #ffffff;
            border: 1px solid #6a0dad;
            font-size: 16px;
        }
        .stDataFrame, .stTable {
            background-color: #2c2c2c;
            color: #ffffff;
        }
        table {
            background-color: #2c2c2c;
            color: #ffffff;
            border: 1px solid #6a0dad;
            font-size: 16px;
        }
        th, td {
            border: 1px solid #6a0dad;
            padding: 10px;
            color: #ffffff;
            font-size: 16px;
        }
        .stSelectbox label, .stTextInput label, .stNumberInput label, .stTextArea label {
            color: #ffffff;
            font-size: 18px;
        }
        /* انتقال سایدبار به سمت راست */
        .css-1d391kg {
            background-color: #1a1a1a;
            color: #ffffff;
            position: fixed;
            right: 0;
            left: auto;
            width: 20rem;
        }
        .stSidebar label {
            color: #ffffff;
            font-size: 18px;
        }
        /* تنظیم فاصله محتوای اصلی */
        .css-18e3th9 {
            padding-right: 22rem;
            padding-left: 1rem;
        }
    </style>
    <link href="https://v1.fontapi.ir/css/Vazir" rel="stylesheet">
""", unsafe_allow_html=True)

# تابع برای نمایش خطاها


def display_error(error_response: Dict):
    try:
        if isinstance(error_response, dict) and "detail" in error_response:
            if isinstance(error_response["detail"], list):
                for error in error_response["detail"]:
                    st.error(f"خطا در {error['loc'][-1]}: {error['msg']}")
            else:
                st.error(error_response["detail"])
        else:
            st.error("خطای ناشناخته: لطفاً دوباره امتحان کنید.")
    except Exception as e:
        st.error(f"خطا در پردازش پاسخ: {str(e)}")

# تابع برای گرفتن لیست از API


# تابع برای حذف آیتم


def delete_item(endpoint: str, item_id: str):
    try:
        response = requests.delete(f"{BASE_URL}/{endpoint}/{item_id}")
        response.raise_for_status()
        st.success(f"با موفقیت حذف شد: {item_id}")
    except requests.RequestException as e:
        display_error({"detail": str(e)})

# تابع برای دریافت اطلاعات آیتم برای ویرایش


def fetch_item(endpoint: str, item_id: str) -> Dict:
    try:
        response = requests.get(f"{BASE_URL}/{endpoint}/{item_id}")
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        st.error(f"خطا در دریافت اطلاعات: {str(e)}")
        return {}


def fetch_data(endpoint: str) -> List[Dict]:
    try:
        response = requests.get(f"{BASE_URL}/{endpoint}")
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        st.error(f"خطا در دریافت داده از API: {str(e)}")
        return []
# تابع برای ارسال فرم (ایجاد یا ویرایش)


def submit_form(endpoint: str, data: Dict, is_edit: bool = False, item_id: str = None):
    try:
        if is_edit:
            response = requests.put(
                f"{BASE_URL}/{endpoint}/{item_id}", json=data)
        else:
            response = requests.post(f"{BASE_URL}/{endpoint}/", json=data)
        response.raise_for_status()
        st.success("با موفقیت ثبت شد!")
        return True
    except requests.RequestException as e:
        try:
            error_detail = response.json()
            display_error(error_detail)
        except:
            st.error(f"خطا: {str(e)}")
        return False


# منوی کناری (حالا در سمت راست)
with st.sidebar:
    st.title("منو")
    section = st.selectbox("بخش مورد نظر", ["دانشجو", "استاد", "درس"])

# عنوان اصلی
st.markdown("<h1 style='text-align: center; color: #ffffff;'>🎓 سیستم مدیریت دانشگاه</h1>",
            unsafe_allow_html=True)
st.markdown("---")

# ---------- دانشجو ----------
if section == "دانشجو":
    st.subheader("👥 مدیریت دانشجو")
    action = st.selectbox("عملیات", ["نمایش", "افزودن", "ویرایش", "حذف"])

    if action == "نمایش":
        students = fetch_data("students")
        if students:
            df = pd.DataFrame(students)[
                ["stid", "fname", "lname", "father", "nid", "department", "major", "birth", "borncity"]]
            df.columns = ["شماره دانشجویی", "نام", "نام خانوادگی", "نام پدر",
                          "کد ملی", "دانشکده", "رشته", "تاریخ تولد", "شهر محل تولد"]
            st.dataframe(df, use_container_width=True)

    elif action == "افزودن":
        with st.form("student_form"):
            student_id = st.text_input("شماره دانشجویی (۱۱ رقم)", max_chars=11)
            fname = st.text_input("نام", max_chars=10)
            lname = st.text_input("نام خانوادگی", max_chars=10)
            father = st.text_input("نام پدر", max_chars=10)
            birth = st.text_input("تاریخ تولد (YYYY/MM/DD)",
                                  placeholder="مثال: 1370/01/01")
            ids_number = st.text_input("سریال شناسنامه (۶ رقم)", max_chars=6)
            ids_letter = st.selectbox("حرف سریال شناسنامه", [
                "آ", "ا", "ب", "پ", "ت", "ث", "ج", "چ", "ح", "خ", "د", "ذ",
                "ر", "ز", "ژ", "س", "ش", "ص", "ض", "ط", "ظ", "ع", "غ", "ف",
                "ق", "ک", "گ", "ل", "م", "ن", "و", "ه", "ی"
            ])
            ids_code = st.text_input("کد سریال شناسنامه (۲ رقم)", max_chars=2)
            borncity = st.selectbox("شهر محل تولد", [
                "تهران", "مشهد", "اصفهان", "کرج", "شیراز", "تبریز", "قم", "اهواز",
                "کرمانشاه", "ارومیه", "رشت", "زاهدان", "همدان", "کرمان", "یزد",
                "اردبیل", "بندرعباس", "اراک", "اسلامشهر", "زنجان", "سنندج",
                "قزوین", "خرم‌آباد", "گرگان", "ساری", "بجنورد", "بوشهر",
                "بیرجند", "ایلام", "شهرکرد", "یاسوج"
            ])
            address = st.text_area("آدرس", max_chars=100)
            postalcode = st.text_input("کد پستی (۱۰ رقم)", max_chars=10)
            cphone = st.text_input("شماره موبایل (۱۱ رقم)", max_chars=11)
            hphone = st.text_input("شماره ثابت (۱۱ رقم)", max_chars=11)
            department = st.selectbox(
                "دانشکده", ["فنی مهندسی", "علوم پایه", "اقتصاد"])
            major = st.selectbox("رشته", [
                "مهندسی کامپیوتر", "مهندسی برق", "مهندسی مکانیک",
                "ریاضی", "فیزیک", "شیمی", "اقتصاد", "مدیریت", "حسابداری"
            ])
            married = st.selectbox("وضعیت تأهل", ["مجرد", "متاهل"])
            nid = st.text_input("کد ملی (۱۰ رقم)", max_chars=10)
            courseids = st.text_input("شناسه دروس (اختیاری)")
            lids = st.text_input("شناسه اساتید (اختیاری)")

            submit_button = st.form_submit_button("افزودن")
            if submit_button:
                student_data = {
                    "stid": student_id,
                    "fname": fname,
                    "lname": lname,
                    "father": father,
                    "birth": birth,
                    "ids_number": ids_number,
                    "ids_letter": ids_letter,
                    "ids_code": ids_code,
                    "borncity": borncity,
                    "address": address,
                    "postalcode": postalcode,
                    "cphone": cphone,
                    "hphone": hphone,
                    "department": department,
                    "major": major,
                    "married": married,
                    "nid": nid,
                    "courseids": courseids,
                    "lids": lids
                }
                submit_form("students", student_data)

    elif action == "ویرایش":
        student_id = st.text_input("شماره دانشجویی برای ویرایش")
        if student_id:
            student = fetch_item("students", student_id)
            if student:
                with st.form("student_edit_form"):
                    fname = st.text_input(
                        "نام", value=student.get("fname", ""), max_chars=10)
                    lname = st.text_input(
                        "نام خانوادگی", value=student.get("lname", ""), max_chars=10)
                    father = st.text_input(
                        "نام پدر", value=student.get("father", ""), max_chars=10)
                    birth = st.text_input(
                        "تاریخ تولد (YYYY/MM/DD)", value=student.get("birth", ""), placeholder="مثال: 1370/01/01")
                    ids_number = st.text_input(
                        "سریال شناسنامه (۶ رقم)", value=student.get("ids_number", ""), max_chars=6)
                    ids_letter = st.selectbox("حرف سریال شناسنامه", [
                        "آ", "ا", "ب", "پ", "ت", "ث", "ج", "چ", "ح", "خ", "د", "ذ",
                        "ر", "ز", "ژ", "س", "ش", "ص", "ض", "ط", "ظ", "ع", "غ", "ف",
                        "ق", "ک", "گ", "ل", "م", "ن", "و", "ه", "ی"
                    ], index=["آ", "ا", "ب", "پ", "ت", "ث", "ج", "چ", "ح", "خ", "د", "ذ",
                              "ر", "ز", "ژ", "س", "ش", "ص", "ض", "ط", "ظ", "ع", "غ", "ف",
                              "ق", "ک", "گ", "ل", "م", "ن", "و", "ه", "ی"].index(student.get("ids_letter", "آ")))
                    ids_code = st.text_input(
                        "کد سریال شناسنامه (۲ رقم)", value=student.get("ids_code", ""), max_chars=2)
                    borncity = st.selectbox("شهر محل تولد", [
                        "تهران", "مشهد", "اصفهان", "کرج", "شیراز", "تبریز", "قم", "اهواز",
                        "کرمانشاه", "ارومیه", "رشت", "زاهدان", "همدان", "کرمان", "یزد",
                        "اردبیل", "بندرعباس", "اراک", "اسلامشهر", "زنجان", "سنندج",
                        "قزوین", "خرم‌آباد", "گرگان", "ساری", "بجنورد", "بوشهر",
                        "بیرجند", "ایلام", "شهرکرد", "یاسوج"
                    ], index=["تهران", "مشهد", "اصفهان", "کرج", "شیراز", "تبریز", "قم", "اهواز",
                              "کرمانشاه", "ارومیه", "رشت", "زاهدان", "همدان", "کرمان", "یزد",
                              "اردبیل", "بندرعباس", "اراک", "اسلامشهر", "زنجان", "سنندج",
                              "قزوین", "خرم‌آباد", "گرگان", "ساری", "بجنورد", "بوشهر",
                              "بیرجند", "ایلام", "شهرکرد", "یاسوج"].index(student.get("borncity", "تهران")))
                    address = st.text_area("آدرس", value=student.get(
                        "address", ""), max_chars=100)
                    postalcode = st.text_input(
                        "کد پستی (۱۰ رقم)", value=student.get("postalcode", ""), max_chars=10)
                    cphone = st.text_input(
                        "شماره موبایل (۱۱ رقم)", value=student.get("cphone", ""), max_chars=11)
                    hphone = st.text_input(
                        "شماره ثابت (۱۱ رقم)", value=student.get("hphone", ""), max_chars=11)
                    department = st.selectbox("دانشکده", ["فنی مهندسی", "علوم پایه", "اقتصاد"],
                                              index=["فنی مهندسی", "علوم پایه", "اقتصاد"].index(student.get("department", "فنی مهندسی")))
                    major = st.selectbox("رشته", [
                        "مهندسی کامپیوتر", "مهندسی برق", "مهندسی مکانیک",
                        "ریاضی", "فیزیک", "شیمی", "اقتصاد", "مدیریت", "حسابداری"
                    ], index=["مهندسی کامپیوتر", "مهندسی برق", "مهندسی مکانیک",
                              "ریاضی", "فیزیک", "شیمی", "اقتصاد", "مدیریت", "حسابداری"].index(student.get("major", "مهندسی کامپیوتر")))
                    married = st.selectbox("وضعیت تأهل", ["مجرد", "متاهل"],
                                           index=["مجرد", "متاهل"].index(student.get("married", "مجرد")))
                    nid = st.text_input(
                        "کد ملی (۱۰ رقم)", value=student.get("nid", ""), max_chars=10)
                    courseids = st.text_input(
                        "شناسه دروس (اختیاری)", value=student.get("courseids", ""))
                    lids = st.text_input(
                        "شناسه اساتید (اختیاری)", value=student.get("lids", ""))

                    submit_button = st.form_submit_button("ویرایش")
                    if submit_button:
                        student_data = {
                            "stid": student_id,
                            "fname": fname,
                            "lname": lname,
                            "father": father,
                            "birth": birth,
                            "ids_number": ids_number,
                            "ids_letter": ids_letter,
                            "ids_code": ids_code,
                            "borncity": borncity,
                            "address": address,
                            "postalcode": postalcode,
                            "cphone": cphone,
                            "hphone": hphone,
                            "department": department,
                            "major": major,
                            "married": married,
                            "nid": nid,
                            "courseids": courseids,
                            "lids": lids
                        }
                        submit_form("students", student_data,
                                    is_edit=True, item_id=student_id)

    elif action == "حذف":
        student_id = st.text_input("شماره دانشجویی برای حذف")
        if st.button("حذف"):
            delete_item("students", student_id)

# ---------- استاد ----------
elif section == "استاد":
    st.subheader("👨‍🏫 مدیریت استاد")
    action = st.selectbox("عملیات", ["نمایش", "افزودن", "ویرایش", "حذف"])

    if action == "نمایش":
        professors = fetch_data("professors")
        if professors:
            df = pd.DataFrame(professors)[
                ["lid", "fname", "lname", "nation_id", "department", "major", "birth_date", "born_city"]]
            df.columns = ["کد استاد", "نام", "نام خانوادگی", "کد ملی",
                          "دانشکده", "رشته", "تاریخ تولد", "شهر محل تولد"]
            st.dataframe(df, use_container_width=True)

    elif action == "افزودن":
        with st.form("professor_form"):
            lid = st.text_input("کد استاد (۶ رقم)", max_chars=6)
            fname = st.text_input("نام", max_chars=10)
            lname = st.text_input("نام خانوادگی", max_chars=10)
            nation_id = st.text_input("کد ملی (۱۰ رقم)", max_chars=10)
            department = st.selectbox(
                "دانشکده", ["فنی مهندسی", "علوم پایه", "اقتصاد"])
            major = st.selectbox("رشته", [
                "مهندسی کامپیوتر", "مهندسی برق", "مهندسی مکانیک", "مهندسی معدن",
                "مهندسی عمران", "مهندسی شهرسازی", "مهندسی پلیمر",
                "ریاضی", "فیزیک", "شیمی", "اقتصاد", "مدیریت", "حسابداری"
            ])
            birth_date = st.text_input(
                "تاریخ تولد (YYYY/MM/DD)", placeholder="مثال: 1370/01/01")
            born_city = st.selectbox("شهر محل تولد", [
                "تهران", "مشهد", "اصفهان", "کرج", "شیراز", "تبریز", "قم", "اهواز",
                "کرمانشاه", "ارومیه", "رشت", "زاهدان", "همدان", "کرمان", "یزد",
                "اردبیل", "بندرعباس", "اراک", "اسلامشهر", "زنجان", "سنندج",
                "قزوین", "خرم‌آباد", "گرگان", "ساری", "بجنورد", "بوشهر",
                "بیرجند", "ایلام", "شهرکرد", "یاسوج"
            ])
            address = st.text_area("آدرس", max_chars=100)
            postal_code = st.text_input("کد پستی (۱۰ رقم)", max_chars=10)
            cphone = st.text_input("شماره موبایل (۱۱ رقم)", max_chars=11)
            hphone = st.text_input("شماره ثابت (۱۱ رقم)", max_chars=11)
            course_ids = st.text_input("شناسه دروس (اختیاری)")

            submit_button = st.form_submit_button("افزودن")
            if submit_button:
                professor_data = {
                    "lid": lid,
                    "fname": fname,
                    "lname": lname,
                    "nation_id": nation_id,
                    "department": department,
                    "major": major,
                    "birth_date": birth_date,
                    "born_city": born_city,
                    "address": address,
                    "postal_code": postal_code,
                    "cphone": cphone,
                    "hphone": hphone,
                    "course_ids": course_ids
                }
                submit_form("professors", professor_data)

    elif action == "ویرایش":
        lid = st.text_input("کد استاد برای ویرایش")
        if lid:
            professor = fetch_item("professors", lid)
            if professor:
                with st.form("professor_edit_form"):
                    fname = st.text_input(
                        "نام", value=professor.get("fname", ""), max_chars=10)
                    lname = st.text_input(
                        "نام خانوادگی", value=professor.get("lname", ""), max_chars=10)
                    nation_id = st.text_input(
                        "کد ملی (۱۰ رقم)", value=professor.get("nation_id", ""), max_chars=10)
                    department = st.selectbox("دانشکده", ["فنی مهندسی", "علوم پایه", "اقتصاد"],
                                              index=["فنی مهندسی", "علوم پایه", "اقتصاد"].index(professor.get("department", "فنی مهندسی")))
                    major = st.selectbox("رشته", [
                        "مهندسی کامپیوتر", "مهندسی برق", "مهندسی مکانیک", "مهندسی معدن",
                        "مهندسی عمران", "مهندسی شهرسازی", "مهندسی پلیمر",
                        "ریاضی", "فیزیک", "شیمی", "اقتصاد", "مدیریت", "حسابداری"
                    ], index=["مهندسی کامپیوتر", "مهندسی برق", "مهندسی مکانیک", "مهندسی معدن",
                              "مهندسی عمران", "مهندسی شهرسازی", "مهندسی پلیمر",
                              "ریاضی", "فیزیک", "شیمی", "اقتصاد", "مدیریت", "حسابداری"].index(professor.get("major", "مهندسی کامپیوتر")))
                    birth_date = st.text_input("تاریخ تولد (YYYY/MM/DD)", value=professor.get(
                        "birth_date", ""), placeholder="مثال: 1370/01/01")
                    born_city = st.selectbox("شهر محل تولد", [
                        "تهران", "مشهد", "اصفهان", "کرج", "شیراز", "تبریز", "قم", "اهواز",
                        "کرمانشاه", "ارومیه", "رشت", "زاهدان", "همدان", "کرمان", "یزد",
                        "اردبیل", "بندرعباس", "اراک", "اسلامشهر", "زنجان", "سنندج",
                        "قزوین", "خرم‌آباد", "گرگان", "ساری", "بجنورد", "بوشهر",
                        "بیرجند", "ایلام", "شهرکرد", "یاسوج"
                    ], index=["تهران", "مشهد", "اصفهان", "کرج", "شیراز", "تبریز", "قم", "اهواز",
                              "کرمانشاه", "ارومیه", "رشت", "زاهدان", "همدان", "کرمان", "یزد",
                              "اردبیل", "بندرعباس", "اراک", "اسلامشهر", "زنجان", "سنندج",
                              "قزوین", "خرم‌آباد", "گرگان", "ساری", "بجنورد", "بوشهر",
                              "بیرجند", "ایلام", "شهرکرد", "یاسوج"].index(professor.get("born_city", "تهران")))
                    address = st.text_area("آدرس", value=professor.get(
                        "address", ""), max_chars=100)
                    postal_code = st.text_input(
                        "کد پستی (۱۰ رقم)", value=professor.get("postal_code", ""), max_chars=10)
                    cphone = st.text_input(
                        "شماره موبایل (۱۱ رقم)", value=professor.get("cphone", ""), max_chars=11)
                    hphone = st.text_input(
                        "شماره ثابت (۱۱ رقم)", value=professor.get("hphone", ""), max_chars=11)
                    course_ids = st.text_input(
                        "شناسه دروس (اختیاری)", value=professor.get("course_ids", ""))

                    submit_button = st.form_submit_button("ویرایش")
                    if submit_button:
                        professor_data = {
                            "lid": lid,
                            "fname": fname,
                            "lname": lname,
                            "nation_id": nation_id,
                            "department": department,
                            "major": major,
                            "birth_date": birth_date,
                            "born_city": born_city,
                            "address": address,
                            "postal_code": postal_code,
                            "cphone": cphone,
                            "hphone": hphone,
                            "course_ids": course_ids
                        }
                        submit_form("professors", professor_data,
                                    is_edit=True, item_id=lid)

    elif action == "حذف":
        lid = st.text_input("کد استاد برای حذف")
        if st.button("حذف"):
            delete_item("professors", lid)

# ---------- درس ----------
elif section == "درس":
    st.subheader("📘 مدیریت درس")
    action = st.selectbox("عملیات", ["نمایش", "افزودن", "ویرایش", "حذف"])

    if action == "نمایش":
        courses = fetch_data("courses")
        if courses:
            df = pd.DataFrame(courses)[
                ["cid", "course_name", "credit", "department"]]
            df.columns = ["کد درس", "نام درس", "واحد", "دانشکده"]
            st.dataframe(df, use_container_width=True)

    elif action == "افزودن":
        with st.form("course_form"):
            course_id = st.text_input("کد درس (۵ رقم)", max_chars=5)
            course_name = st.text_input("نام درس", max_chars=25)
            credit = st.number_input(
                "واحد (۱ تا ۴)", min_value=1, max_value=4, step=1)
            department = st.selectbox(
                "دانشکده", ["فنی مهندسی", "علوم پایه", "اقتصاد"])

            submit_button = st.form_submit_button("افزودن")
            if submit_button:
                course_data = {
                    "cid": course_id,
                    "course_name": course_name,
                    "credit": credit,
                    "department": department
                }
                submit_form("courses", course_data)

    elif action == "ویرایش":
        course_id = st.text_input("کد درس برای ویرایش")
        if course_id:
            course = fetch_item("courses", course_id)
            if course:
                with st.form("course_edit_form"):
                    course_name = st.text_input(
                        "نام درس", value=course.get("course_name", ""), max_chars=25)
                    credit = st.number_input(
                        "واحد (۱ تا ۴)", min_value=1, max_value=4, step=1, value=course.get("credit", 1))
                    department = st.selectbox("دانشکده", ["فنی مهندسی", "علوم پایه", "اقتصاد"],
                                              index=["فنی مهندسی", "علوم پایه", "اقتصاد"].index(course.get("department", "فنی مهندسی")))

                    submit_button = st.form_submit_button("ویرایش")
                    if submit_button:
                        course_data = {
                            "cid": course_id,
                            "course_name": course_name,
                            "credit": credit,
                            "department": department
                        }
                        submit_form("courses", course_data,
                                    is_edit=True, item_id=course_id)

    elif action == "حذف":
        course_id = st.text_input("کد درس برای حذف")
        if st.button("حذف"):
            delete_item("courses", course_id)

# فوتر
st.markdown("---")
st.markdown(
    """
    <p style='text-align: center; color: #6a0dad; font-size: 20px;'>ساخته شده توسط هیراد طولابی ✨</p>
    """,
    unsafe_allow_html=True
)
