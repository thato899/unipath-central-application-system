"""Local UniPath demo API with undergraduate programme names from UP's 2026 Yearbook.

Admission thresholds and outcomes are demo data and are not official UP requirements or decisions.
"""
from __future__ import annotations

import json
import mimetypes
import uuid
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, unquote, urlparse

ROOT = Path(__file__).resolve().parent
STATIC = ROOT / "static"
HOST, PORT = "127.0.0.1", 8000

UNIVERSITIES = [
    {"id": "up", "name": "University of Pretoria", "region": "Gauteng", "sample": False},
    {"id": "sample-university", "name": "Central Demo University", "region": "South Africa", "sample": True},
]

# Initial undergraduate programme entries from UP's published Yearbook.
# The minimum thresholds below are deliberately illustrative, not official admission criteria.
PROGRAMMES = [
    ("bcom-accounting", "BCom in Accounting Sciences", "BCom Accounting Sciences", "Economic and Management Sciences", "Develop financial reporting, audit and business skills.", ["Chartered accountant (with further study and professional exams)", "Auditor", "Financial analyst"], 36, 60),
    ("bcom-economics", "BCom specialising in Economics", "BCom Economics", "Economic and Management Sciences", "Study markets, public policy and how economies work.", ["Economist", "Policy analyst", "Market researcher"], 32, 50),
    ("bed-foundation", "Bachelor of Education in Foundation Phase Teaching", "BEd Foundation Phase", "Education", "Prepare to teach young learners in the foundation phase.", ["Foundation phase teacher", "Learning support practitioner", "Education materials developer"], 28, 40),
    ("beng-civil", "BEng in Civil Engineering 4-year programme", "BEng Civil Engineering", "Engineering, Built Environment and IT", "Design and maintain infrastructure such as roads, bridges and water systems.", ["Civil engineer", "Transport planner", "Water infrastructure specialist"], 35, 65),
    ("bsc-computer-science", "BSc in Computer Science", "BSc Computer Science", "Engineering, Built Environment and IT", "Build software, understand data and solve problems with computing.", ["Software developer", "Data analyst", "Cybersecurity specialist"], 34, 60),
    ("bnursing", "Bachelor of Nursing Science", "BNursing Science", "Health Sciences", "Learn to provide evidence-based care across health settings.", ["Professional nurse", "Community health practitioner", "Clinical educator"], 30, 50),
    ("ba-audiology", "BA in Audiology", "BA Audiology", "Humanities", "Study hearing, communication and rehabilitation services.", ["Audiologist (subject to professional registration)", "Hearing therapist", "Audiology researcher"], 32, 50),
    ("ba", "Bachelor of Arts 3-year programme", "BA 3-year programme", "Humanities", "Combine humanities and social science fields to understand people and society.", ["Communications officer", "Research assistant", "Public service professional"], 30, 50),
    ("llb", "Bachelor of Laws", "LLB", "Law", "Build a foundation in legal systems, reasoning and advocacy.", ["Attorney (after required further training)", "Legal adviser", "Policy researcher"], 35, 60),
    ("bsc-actuarial", "BSc in Actuarial and Financial Mathematics", "BSc Actuarial and Financial Mathematics", "Natural and Agricultural Sciences", "Use mathematics and statistics to model risk and financial decisions.", ["Actuarial analyst", "Risk analyst", "Quantitative researcher"], 38, 70),
    ("bsc-biochemistry", "BSc in Biochemistry", "BSc Biochemistry", "Natural and Agricultural Sciences", "Explore the chemistry of living systems and laboratory science.", ["Laboratory analyst", "Biotechnology researcher", "Quality assurance scientist"], 32, 50),
    ("bth", "Bachelor of Theology", "BTh", "Theology and Religion", "Study religious traditions, ethics and community leadership.", ["Community programme coordinator", "Pastoral worker", "Religious studies educator"], 28, 40),
    ("bvsc", "Bachelor of Veterinary Science", "BVSc", "Veterinary Science", "Train in animal health, disease prevention and veterinary practice.", ["Veterinarian (subject to professional registration)", "Animal health researcher", "Veterinary public health specialist"], 38, 70),
]

# Additional undergraduate choices from UP's 2026 Yearbook lists. Career examples are
# orientation only; the demo's admission thresholds remain illustrative.
PROGRAMMES += [
    ("badmin-public", "BAdmin specialising in Public Management and International Relations", "BAdmin Public Management and International Relations", "Economic and Management Sciences", "Study public institutions, policy, administration and international relations.", ["Public administrator", "Policy analyst", "Diplomatic service officer"], 30, 40),
    ("bcom-business", "BCom specialising in Business Management", "BCom Business Management", "Economic and Management Sciences", "Build knowledge of business strategy, organisations and management.", ["Business manager", "Management consultant", "Entrepreneur"], 30, 40),
    ("bcom-marketing", "BCom specialising in Marketing Management", "BCom Marketing Management", "Economic and Management Sciences", "Study how organisations understand customers and build markets.", ["Marketing specialist", "Brand manager", "Market researcher"], 30, 40),
    ("bcom-supply-chain", "BCom specialising in Supply Chain Management", "BCom Supply Chain Management", "Economic and Management Sciences", "Learn how organisations plan sourcing, logistics and distribution.", ["Supply chain analyst", "Logistics manager", "Procurement specialist"], 30, 40),
    ("bed-early-childhood", "BEd in Early Childhood Care and Education", "BEd Early Childhood Care and Education", "Education", "Prepare to support care and education for young children from birth to four.", ["Early childhood educator", "Early learning centre coordinator", "Curriculum support practitioner"], 28, 40),
    ("bed-intermediate", "BEd in Intermediate Phase Teaching", "BEd Intermediate Phase Teaching", "Education", "Prepare to teach learners in the intermediate phase of schooling.", ["Intermediate phase teacher", "Learning support teacher", "Education programme facilitator"], 28, 40),
    ("bed-senior-fet", "BEd in Senior Phase and Further Education and Training Teaching", "BEd Senior Phase and FET Teaching", "Education", "Prepare to teach in the senior phase and further education and training band.", ["Secondary school teacher", "Subject specialist teacher", "Education materials developer"], 28, 40),
    ("bit-information-systems", "Bachelor of Information Technology in Information Systems", "BIT Information Systems", "Engineering, Built Environment and IT", "Combine programming, systems analysis, databases and organisational problem solving.", ["Business analyst", "Systems analyst", "Software developer"], 30, 50),
    ("bis-multimedia", "Bachelor of Information Science specialising in Multimedia", "BIS Multimedia", "Engineering, Built Environment and IT", "Explore digital media, information design and multimedia publishing.", ["Multimedia designer", "Digital content producer", "User experience assistant"], 28, 40),
    ("bis-publishing", "Bachelor of Information Science specialising in Publishing", "BIS Publishing", "Engineering, Built Environment and IT", "Learn about publishing, information products and digital content.", ["Publishing coordinator", "Content editor", "Digital publishing specialist"], 28, 40),
    ("bsc-it-iks", "BSc in Information Technology in Information and Knowledge Systems", "BSc IT Information and Knowledge Systems", "Engineering, Built Environment and IT", "Study computing, information systems and knowledge technologies.", ["Data scientist", "Knowledge manager", "IT systems developer"], 32, 60),
    ("bsc-architecture", "BSc in Architecture", "BSc Architecture", "Engineering, Built Environment and IT", "Explore design, buildings and the built environment as a foundation for architectural study.", ["Architectural designer", "Urban design assistant", "Building technology specialist"], 32, 50),
    ("bsc-quantity-surveying", "BSc in Quantity Surveying", "BSc Quantity Surveying", "Engineering, Built Environment and IT", "Learn to plan and manage the costs of construction projects.", ["Quantity surveyor (with required professional pathway)", "Cost consultant", "Construction project estimator"], 30, 50),
    ("bchd", "Bachelor of Dental Surgery", "BChD", "Health Sciences", "Train in oral health, prevention and dental care.", ["Dentist (subject to professional registration)", "Oral health researcher", "Community dental health practitioner"], 35, 60),
    ("mbchb", "Bachelor of Medicine and Surgery", "MBChB", "Health Sciences", "Study medicine through scientific learning and supervised clinical training.", ["Medical doctor (after required internship and registration)", "Clinical researcher", "Public health practitioner"], 38, 70),
    ("bphysio", "Bachelor of Physiotherapy", "BPhysio", "Health Sciences", "Learn to assess movement and support recovery and physical function.", ["Physiotherapist (subject to professional registration)", "Rehabilitation practitioner", "Sports health practitioner"], 34, 60),
    ("bdietetics", "Bachelor of Dietetics", "BDietetics", "Health Sciences", "Study nutrition science and dietary care for individuals and communities.", ["Dietitian (subject to professional registration)", "Community nutrition specialist", "Food service manager"], 32, 50),
    ("ba-fine-arts", "BA in Fine Arts 4-year programme", "BA Fine Arts", "Humanities", "Develop studio practice and critical understanding of visual arts.", ["Visual artist", "Arts educator", "Gallery or museum practitioner"], 28, 40),
    ("ba-information-design", "BA in Information Design", "BA Information Design", "Humanities", "Use visual communication and design to make information clear and engaging.", ["Information designer", "Graphic designer", "Digital communication designer"], 30, 40),
    ("bdram", "Bachelor of Drama", "BDram", "Humanities", "Study performance, theatre making and the creative industries.", ["Actor", "Theatre director", "Arts and production coordinator"], 28, 40),
    ("bmus", "Bachelor of Music", "BMus", "Humanities", "Develop musical performance, theory and creative practice.", ["Musician", "Music educator", "Composer or music producer"], 28, 40),
    ("bsw", "Bachelor of Social Work", "BSW", "Humanities", "Prepare to support individuals, families and communities through social work.", ["Social worker (subject to professional registration)", "Community development practitioner", "Family support worker"], 30, 40),
    ("bpolsci-international", "BPolSci specialising in International Studies", "BPolSci International Studies", "Humanities", "Study global politics, international relations and public affairs.", ["Diplomatic service officer", "International relations analyst", "Policy researcher"], 30, 40),
    ("bsc-geology", "BSc in Geology", "BSc Geology", "Natural and Agricultural Sciences", "Study Earth materials, processes and geological resources.", ["Geologist", "Exploration geoscientist", "Environmental consultant"], 32, 50),
    ("bsc-microbiology", "BSc in Microbiology", "BSc Microbiology", "Natural and Agricultural Sciences", "Explore microorganisms and their roles in health, industry and ecosystems.", ["Microbiologist", "Laboratory scientist", "Biotechnology researcher"], 32, 50),
    ("bsc-food-science", "BSc in Food Science", "BSc Food Science", "Natural and Agricultural Sciences", "Apply science to food production, safety, quality and innovation.", ["Food scientist", "Quality assurance specialist", "Food safety analyst"], 30, 50),
    ("bsc-physics", "BSc in Physics", "BSc Physics", "Natural and Agricultural Sciences", "Use mathematics and experiments to understand physical systems.", ["Physicist", "Data analyst", "Research scientist"], 32, 60),
    ("bsc-mathematics", "BSc in Mathematics", "BSc Mathematics", "Natural and Agricultural Sciences", "Build mathematical reasoning for science, technology and quantitative work.", ["Mathematical analyst", "Statistician", "Quantitative researcher"], 34, 60),
    ("bsc-zoology", "BSc in Zoology", "BSc Zoology", "Natural and Agricultural Sciences", "Study animal biology, biodiversity and ecosystems.", ["Zoologist", "Conservation scientist", "Ecology researcher"], 30, 50),
    ("bscag-animal-science", "BScAgric in Animal Science", "BScAgric Animal Science", "Natural and Agricultural Sciences", "Study animal production, welfare and agricultural systems.", ["Animal scientist", "Livestock production adviser", "Agricultural researcher"], 30, 50),
    ("bscag-agribusiness", "BScAgric in Agricultural Economics in Agribusiness Management", "BScAgric Agribusiness Management", "Natural and Agricultural Sciences", "Connect agricultural economics with farm and agribusiness management.", ["Agribusiness analyst", "Agricultural economist", "Farm business manager"], 30, 50),
    ("bdiv", "Bachelor of Divinity", "BDiv", "Theology and Religion", "Study theology, scripture and ministry with a focus on service and community.", ["Minister (subject to faith community requirements)", "Community programme leader", "Theology researcher"], 28, 40),
    ("bvetnurs", "Bachelor of Veterinary Nursing", "BVetNurs", "Veterinary Science", "Train in animal nursing and clinical support for veterinary care.", ["Veterinary nurse (subject to professional registration)", "Animal welfare practitioner", "Veterinary clinic nurse"], 30, 50),
]

# Remaining undergraduate degree entries shown on the 2026 Yearbook faculty pages.
# The labels and careers are catalogue content; admission values are generated demo values.
YEARBOOK_PROGRAMMES = [
    ("bcom-3year", "BCom 3-year programme", "Economic and Management Sciences"),
    ("bcom-4year", "BCom 4-year programme", "Economic and Management Sciences"),
    ("bcom-agribusiness", "BCom specialising in Agribusiness Management", "Economic and Management Sciences"),
    ("bcom-econometrics", "BCom specialising in Econometrics", "Economic and Management Sciences"),
    ("bcom-financial-management", "BCom specialising in Financial Management Sciences", "Economic and Management Sciences"),
    ("bcom-hr", "BCom specialising in Human Resource Management", "Economic and Management Sciences"),
    ("bcom-information-systems", "BCom specialising in Information Systems", "Economic and Management Sciences"),
    ("bcom-investment", "BCom specialising in Investment Management", "Economic and Management Sciences"),
    ("bcom-law", "BCom specialising in Law", "Economic and Management Sciences"),
    ("bcom-statistics", "BCom specialising in Statistics and Data Science", "Economic and Management Sciences"),
    ("bis", "Bachelor of Information Science", "Engineering, Built Environment and IT"),
    ("btrp", "Bachelor of Town and Regional Planning", "Engineering, Built Environment and IT"),
    ("beng-chemical-4", "BEng in Chemical Engineering 4-year programme", "Engineering, Built Environment and IT"),
    ("beng-chemical-5", "BEng in Chemical Engineering 5-year programme", "Engineering, Built Environment and IT"),
    ("beng-civil-5", "BEng in Civil Engineering 5-year programme", "Engineering, Built Environment and IT"),
    ("beng-computer-4", "BEng in Computer Engineering 4-year programme", "Engineering, Built Environment and IT"),
    ("beng-computer-5", "BEng in Computer Engineering 5-year programme", "Engineering, Built Environment and IT"),
    ("beng-electrical-4", "BEng in Electrical Engineering 4-year programme", "Engineering, Built Environment and IT"),
    ("beng-electrical-5", "BEng in Electrical Engineering 5-year programme", "Engineering, Built Environment and IT"),
    ("beng-electronic-4", "BEng in Electronic Engineering 4-year programme", "Engineering, Built Environment and IT"),
    ("beng-electronic-5", "BEng in Electronic Engineering 5-year programme", "Engineering, Built Environment and IT"),
    ("beng-industrial-4", "BEng in Industrial Engineering 4-year programme", "Engineering, Built Environment and IT"),
    ("beng-industrial-5", "BEng in Industrial Engineering 5-year programme", "Engineering, Built Environment and IT"),
    ("beng-mechanical-4", "BEng in Mechanical Engineering 4-year programme", "Engineering, Built Environment and IT"),
    ("beng-mechanical-5", "BEng in Mechanical Engineering 5-year programme", "Engineering, Built Environment and IT"),
    ("beng-metallurgical-4", "BEng in Metallurgical Engineering 4-year programme", "Engineering, Built Environment and IT"),
    ("beng-metallurgical-5", "BEng in Metallurgical Engineering 5-year programme", "Engineering, Built Environment and IT"),
    ("beng-mining-4", "BEng in Mining Engineering 4-year programme", "Engineering, Built Environment and IT"),
    ("beng-mining-5", "BEng in Mining Engineering 5-year programme", "Engineering, Built Environment and IT"),
    ("bsc-construction-management", "BSc in Construction Management", "Engineering, Built Environment and IT"),
    ("bsc-real-estate", "BSc in Real Estate", "Engineering, Built Environment and IT"),
    ("bachelor-of-occupational-therapy", "Bachelor of Occupational Therapy", "Health Sciences"),
    ("bachelor-of-oral-hygiene", "Bachelor of Oral Hygiene", "Health Sciences"),
    ("bachelor-of-radiography", "Bachelor of Radiography in Diagnostics", "Health Sciences"),
    ("bachelor-of-sports-science", "Bachelor of Sports Science", "Health Sciences"),
    ("bachelor-of-clinical-medical-practice", "Bachelor of Clinical Medical Practice", "Health Sciences"),
    ("ba-fine-arts-5", "BA in Fine Arts 5-year programme", "Humanities"),
    ("ba-speech-language-pathology", "BA in Speech-Language Pathology", "Humanities"),
    ("ba-languages", "BA specialising in Languages", "Humanities"),
    ("ba-law", "BA specialising in Law", "Humanities"),
    ("ba-ppe", "BA specialising in Philosophy, Politics and Economics", "Humanities"),
    ("ba-visual-studies", "BA specialising in Visual Studies", "Humanities"),
    ("ba-4year", "Bachelor of Arts 4-year programme", "Humanities"),
    ("bdram-4year", "Bachelor of Drama 4-year programme", "Humanities"),
    ("bmus-5year", "Bachelor of Music 5-year programme", "Humanities"),
    ("bpoolsci-political", "BPolSci specialising in Political Studies", "Humanities"),
    ("bsoc-sci-heritage", "BSocSci in Heritage and Cultural Sciences option Heritage and Cultural Tourism", "Humanities"),
    ("bsoc-sci-industrial-sociology", "BSocSci specialising in Industrial Sociology and Labour Studies", "Humanities"),
    ("bcon-sci-clothing", "Bachelor of Consumer Science specialising in Clothing Retail Management", "Natural and Agricultural Sciences"),
    ("bcon-sci-food", "Bachelor of Consumer Science specialising in Food Management", "Natural and Agricultural Sciences"),
    ("bsc-applied-mathematics", "BSc in Applied Mathematics", "Natural and Agricultural Sciences"),
    ("bsc-biotechnology", "BSc in Biotechnology", "Natural and Agricultural Sciences"),
    ("bsc-chemistry", "BSc in Chemistry", "Natural and Agricultural Sciences"),
    ("bsc-chemistry-4", "BSc in Chemistry 4-year programme", "Natural and Agricultural Sciences"),
    ("bsc-ecology", "BSc in Ecology", "Natural and Agricultural Sciences"),
    ("bsc-ecology-4", "BSc in Ecology 4-year programme", "Natural and Agricultural Sciences"),
    ("bsc-entomology", "BSc in Entomology", "Natural and Agricultural Sciences"),
    ("bsc-env-engineering-geology", "BSc in Environmental and Engineering Geology", "Natural and Agricultural Sciences"),
    ("bsc-culinary-science", "BSc in Food Management specialising in Culinary Science", "Natural and Agricultural Sciences"),
    ("bsc-food-nutrition", "BSc in Food Management specialising in Nutrition", "Natural and Agricultural Sciences"),
    ("bsc-genetics", "BSc in Genetics", "Natural and Agricultural Sciences"),
    ("bsc-geography-environmental", "BSc in Geography option Geography and Environmental Science", "Natural and Agricultural Sciences"),
    ("bsc-geoinformatics", "BSc in Geoinformatics", "Natural and Agricultural Sciences"),
    ("bsc-geoinformatics-4", "BSc in Geoinformatics 4-year programme", "Natural and Agricultural Sciences"),
    ("bsc-geology-4", "BSc in Geology 4-year programme", "Natural and Agricultural Sciences"),
    ("bsc-human-genetics", "BSc in Human Genetics", "Natural and Agricultural Sciences"),
    ("bsc-human-physiology", "BSc in Human Physiology", "Natural and Agricultural Sciences"),
    ("bsc-human-physiology-4", "BSc in Human Physiology 4-year programme", "Natural and Agricultural Sciences"),
    ("bsc-human-physiology-genetics-psychology", "BSc in Human Physiology, Genetics and Psychology", "Natural and Agricultural Sciences"),
    ("bsc-mathematical-statistics", "BSc in Mathematical Statistics", "Natural and Agricultural Sciences"),
    ("bsc-mathematics-4", "BSc in Mathematics 4-year programme", "Natural and Agricultural Sciences"),
    ("bsc-medical-sciences", "BSc in Medical Sciences", "Natural and Agricultural Sciences"),
    ("bsc-meteorology", "BSc in Meteorology", "Natural and Agricultural Sciences"),
    ("bsc-meteorology-4", "BSc in Meteorology 4-year programme", "Natural and Agricultural Sciences"),
    ("bsc-physics-4", "BSc in Physics 4-year programme", "Natural and Agricultural Sciences"),
    ("bsc-plant-science", "BSc in Plant Science", "Natural and Agricultural Sciences"),
    ("bscag-applied-plant-soil", "BScAgric in Applied Plant and Soil Sciences", "Natural and Agricultural Sciences"),
    ("bscag-applied-plant-soil-5", "BScAgric in Applied Plant and Soil Sciences 5-year programme", "Natural and Agricultural Sciences"),
    ("bscag-plant-pathology", "BScAgric in Plant Pathology", "Natural and Agricultural Sciences"),
    ("bscag-plant-pathology-5", "BScAgric in Plant Pathology 5-year programme", "Natural and Agricultural Sciences"),
]

FACULTY_COPY = {
    "Economic and Management Sciences": ("Explore business, economics, finance and public management.", ["Business analyst", "Financial services professional", "Management or policy specialist"]),
    "Engineering, Built Environment and IT": ("Study engineering, information technology and the built environment.", ["Engineer or technologist", "Software or systems specialist", "Built environment professional"]),
    "Health Sciences": ("Prepare for health, clinical, rehabilitation and wellness careers.", ["Health professional (where registration applies)", "Clinical or rehabilitation practitioner", "Health researcher"]),
    "Humanities": ("Study society, culture, communication, creative practice and human behaviour.", ["Communications or arts professional", "Educator or researcher", "Community or public service professional"]),
    "Natural and Agricultural Sciences": ("Explore natural sciences, mathematics, agriculture and the environment.", ["Scientist or researcher", "Environmental or agricultural specialist", "Data and laboratory analyst"]),
}
FACULTY_DEMO_THRESHOLDS = {
    "Economic and Management Sciences": (30, 40),
    "Engineering, Built Environment and IT": (32, 60),
    "Health Sciences": (34, 60),
    "Humanities": (28, 40),
    "Natural and Agricultural Sciences": (32, 60),
}
for programme_id, title, faculty in YEARBOOK_PROGRAMMES:
    description, careers = FACULTY_COPY[faculty]
    aps, mathematics = FACULTY_DEMO_THRESHOLDS[faculty]
    PROGRAMMES.append((programme_id, title, title, faculty, description, careers, aps, mathematics))

COURSES = []
for course_id, name, short_name, faculty, description, careers, aps, math in PROGRAMMES:
    COURSE = {
        "id": course_id, "name": name, "short_name": short_name, "faculty": faculty,
        "description": description, "careers": careers,
        "catalogue_source": "Representative UP programme name; verify current details with UP.",
        "matches": [
            {"university_id": "up", "aps": aps, "mathematics": math, "english": 50, "upgrade_path": True},
            {"university_id": "sample-university", "aps": max(24, aps - 3), "mathematics": max(40, math - 10), "english": 45, "upgrade_path": True},
        ],
    }
    COURSES.append(COURSE)

APPLICATIONS: list[dict] = []
RESIDENCE_APPLICATIONS: list[dict] = []

def json_bytes(value: object) -> bytes:
    return json.dumps(value, ensure_ascii=False).encode("utf-8")

def university_for(university_id: str) -> dict | None:
    return next((u for u in UNIVERSITIES if u["id"] == university_id), None)

def course_for(course_id: str) -> dict | None:
    return next((c for c in COURSES if c["id"] == course_id), None)

def match_status(requirements: dict, marks: dict, upgrading: bool) -> str:
    meets = marks.get("aps", 0) >= requirements["aps"] and marks.get("mathematics", 0) >= requirements["mathematics"] and marks.get("english", 0) >= requirements["english"]
    if meets:
        return "meets_requirements"
    return "apply_while_upgrading" if upgrading and requirements["upgrade_path"] else "does_not_match"

class DemoHandler(BaseHTTPRequestHandler):
    server_version = "UniPathDemo/1.0"

    def _send(self, status: int, body: bytes, content_type: str) -> None:
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)

    def _json(self, status: int, value: object) -> None:
        self._send(status, json_bytes(value), "application/json; charset=utf-8")

    def _read_json(self) -> dict:
        length = int(self.headers.get("Content-Length", "0"))
        if length <= 0 or length > 100_000:
            raise ValueError("Send a JSON request body under 100 KB.")
        data = json.loads(self.rfile.read(length).decode("utf-8"))
        if not isinstance(data, dict):
            raise ValueError("The request body must be a JSON object.")
        return data

    @staticmethod
    def _number(query: dict, key: str) -> int:
        try:
            return max(0, min(100, int(query.get(key, ["0"])[0])))
        except (TypeError, ValueError):
            return 0

    def do_GET(self) -> None:
        parsed = urlparse(self.path)
        path, query = unquote(parsed.path), parse_qs(parsed.query)
        if path == "/api/health":
            return self._json(200, {"status": "ok", "demo": True})
        if path == "/api/universities":
            return self._json(200, {"universities": UNIVERSITIES, "sample_data": True})
        if path == "/api/courses":
            courses = [{k: v for k, v in c.items() if k != "matches"} | {"match_count": len(c["matches"])} for c in COURSES]
            return self._json(200, {"courses": courses, "sample_data": True, "admission_thresholds_illustrative": True})
        if path.startswith("/api/courses/") and path.endswith("/matches"):
            course = course_for(path.removeprefix("/api/courses/").removesuffix("/matches").strip("/"))
            if not course:
                return self._json(404, {"error": "Course not found."})
            marks = {k: self._number(query, k) for k in ("aps", "mathematics", "english")}
            upgrading = query.get("upgrading", ["false"])[0].lower() == "true"
            results = []
            for requirement in course["matches"]:
                uni = university_for(requirement["university_id"])
                if uni:
                    results.append({"university": uni, "requirements": {k: requirement[k] for k in ("aps", "mathematics", "english")}, "status": match_status(requirement, marks, upgrading), "requirements_illustrative": True})
            return self._json(200, {"course_id": course["id"], "matches": results, "marks_used": marks, "sample_data": True})
        if path == "/api/applications":
            return self._json(200, {"applications": APPLICATIONS, "sample_data": True})
        if path == "/api/residence":
            return self._json(200, {"residence_applications": RESIDENCE_APPLICATIONS, "sample_data": True})
        if path == "/api/funding-plan":
            accepted = next((app for app in APPLICATIONS if app["status"] == "accepted"), None)
            if not accepted:
                return self._json(200, {"status": "no_accepted_offer", "sample_data": True, "sent_to_nsfas": False})
            residence = next((item for item in RESIDENCE_APPLICATIONS if item["application_id"] == accepted["id"]), None)
            return self._json(200, {
                "status": "summary_ready_demo" if residence else "waiting_for_residence",
                "university_name": accepted["university_name"], "course_name": accepted["course_name"],
                "application_id": accepted["id"],
                "residence_status": residence["status"] if residence else "not_submitted",
                "residence_preference": residence["preference"] if residence else None,
                "sample_data": True, "sent_to_nsfas": False,
            })
        return self._serve_static(path)

    def do_POST(self) -> None:
        path = urlparse(self.path).path
        try:
            body = self._read_json()
        except (ValueError, json.JSONDecodeError, UnicodeDecodeError) as exc:
            return self._json(400, {"error": str(exc)})
        if path == "/api/applications":
            course, marks = course_for(str(body.get("course_id", ""))), body.get("marks", {})
            if not course or not isinstance(marks, dict):
                return self._json(400, {"error": "Choose a valid course and provide marks."})
            ids = body.get("university_ids", [])
            if not isinstance(ids, list) or not ids:
                return self._json(400, {"error": "Select at least one university."})
            subjects = marks.get("subjects")
            if not isinstance(subjects, dict) or len(subjects) != 7 or "Life Orientation" not in subjects or len({str(name).strip().casefold() for name in subjects}) != 7:
                return self._json(400, {"error": "A matric record must include seven unique subjects including Life Orientation."})
            try:
                aps, mathematics, english = (int(marks.get(key, -1)) for key in ("aps", "mathematics", "english"))
                subject_marks = [int(value) for value in subjects.values()]
            except (TypeError, ValueError):
                return self._json(400, {"error": "APS and all subject marks must be numbers."})
            if not 0 <= aps <= 50 or any(not 0 <= value <= 100 for value in [mathematics, english, *subject_marks]):
                return self._json(400, {"error": "APS must be 0–50 and each subject mark must be 0–100."})
            marks["aps"], marks["mathematics"], marks["english"] = aps, mathematics, english
            student_name = str(body.get("student_name", "")).strip()
            if not student_name or len(student_name) > 80:
                return self._json(400, {"error": "Enter a student name of 1–80 characters."})
            if len(ids) != len(set(map(str, ids))):
                return self._json(400, {"error": "Choose each university at most once."})
            allowed = {m["university_id"]: m for m in course["matches"]}
            destinations = []
            for uid in ids:
                req, uni = allowed.get(str(uid)), university_for(str(uid))
                if not req or not uni:
                    return self._json(400, {"error": "One selected university does not offer this course."})
                status = match_status(req, marks, bool(body.get("upgrading", False)))
                if status == "does_not_match":
                    return self._json(400, {"error": "This selection is outside the match or upgrading path."})
                if any(a["course_id"] == course["id"] and a["university_id"] == uni["id"] for a in APPLICATIONS):
                    return self._json(409, {"error": "An application for this course and university already exists in this demo."})
                destinations.append(uni)
            created = []
            for uni in destinations:
                app = {"id": str(uuid.uuid4())[:8], "course_id": course["id"], "course_name": course["short_name"], "university_id": uni["id"], "university_name": uni["name"], "student_name": student_name, "status": "offer_received", "decision": None, "demo_response": True, "sample_data": True}
                APPLICATIONS.append(app); created.append(app)
            return self._json(201, {"applications": created, "sample_data": True})
        if path.startswith("/api/applications/") and path.endswith("/residence"):
            app_id = path.removeprefix("/api/applications/").removesuffix("/residence").strip("/")
            app = next((a for a in APPLICATIONS if a["id"] == app_id), None)
            if not app or app["status"] != "accepted":
                return self._json(409, {"error": "Residence applications are available only after accepting an offer."})
            if any(item["application_id"] == app_id for item in RESIDENCE_APPLICATIONS):
                return self._json(409, {"error": "A residence request has already been recorded for this accepted offer."})
            preference = body.get("preference")
            if preference not in {"On-campus residence", "Off-campus accommodation support", "Either option"}:
                return self._json(400, {"error": "Choose a residence preference."})
            accommodation_needs = str(body.get("accommodation_needs", "")).strip()
            if len(accommodation_needs) > 500:
                return self._json(400, {"error": "Accommodation notes must be 500 characters or fewer."})
            residence = {
                "id": str(uuid.uuid4())[:8], "application_id": app["id"],
                "university_id": app["university_id"], "university_name": app["university_name"],
                "course_name": app["course_name"], "preference": preference,
                "accommodation_needs": accommodation_needs, "status": "request_recorded_demo",
                "sample_data": True,
            }
            RESIDENCE_APPLICATIONS.append(residence)
            return self._json(201, {"residence_application": residence, "sample_data": True})
        if path.startswith("/api/applications/") and path.endswith("/decision"):
            app_id = path.removeprefix("/api/applications/").removesuffix("/decision").strip("/")
            decision = body.get("decision")
            app = next((a for a in APPLICATIONS if a["id"] == app_id), None)
            if decision not in {"accepted", "rejected"} or not app or app["status"] != "offer_received":
                return self._json(400, {"error": "Choose a valid decision for an available demo offer."})
            if decision == "accepted" and any(other["status"] == "accepted" for other in APPLICATIONS):
                return self._json(409, {"error": "Only one offer can be accepted in this single-student demo."})
            app["decision"], app["status"] = decision, decision
            return self._json(200, {"application": app, "sample_data": True})
        return self._json(404, {"error": "API endpoint not found."})

    def _serve_static(self, path: str) -> None:
        relative = "index.html" if path in {"", "/"} else path.lstrip("/")
        target = (STATIC / relative).resolve()
        try:
            target.relative_to(STATIC.resolve())
        except ValueError:
            return self._json(403, {"error": "Path is outside the static directory."})
        if not target.is_file():
            return self._json(404, {"error": "Page not found."})
        content_type = mimetypes.guess_type(target.name)[0] or "application/octet-stream"
        if content_type.startswith("text/") or content_type in {"application/javascript", "application/json"}:
            content_type += "; charset=utf-8"
        self._send(200, target.read_bytes(), content_type)

    def log_message(self, format: str, *args: object) -> None:
        print(f"[{self.log_date_time_string()}] {format % args}")

if __name__ == "__main__":
    from dotenv import load_dotenv
    from django.core.management import execute_from_command_line
    load_dotenv(ROOT / ".env")
    import os
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "unipath_project.settings")
    execute_from_command_line(["manage.py", "runserver", "127.0.0.1:8000"])
