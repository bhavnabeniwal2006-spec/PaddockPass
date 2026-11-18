
from flask import Flask, render_template, abort, request, redirect, url_for, session
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = "paddock-pass-demo-secret-key"

DATABASE = "paddockpass.db"


def init_db():
    conn = sqlite3.connect(DATABASE)

    conn.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL
        )
    """)
    conn.execute("""
    CREATE TABLE IF NOT EXISTS favourites (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        driver_slug TEXT NOT NULL,
        UNIQUE(user_id, driver_slug)
    )
    """)
    conn.commit()
    conn.close()


init_db()

@app.route("/signup", methods=["GET", "POST"])
def signup():
    message = ""

    if request.method == "POST":
        name = request.form["name"].strip()
        email = request.form["email"].strip().lower()
        password = request.form["password"]

        if len(password) < 6:
            message = "Password must be at least 6 characters."

        else:
            conn = sqlite3.connect(DATABASE)

            try:
                password_hash = generate_password_hash(password)

                conn.execute(
                    "INSERT INTO users (name, email, password_hash) VALUES (?, ?, ?)",
                    (name, email, password_hash)
                )

                conn.commit()
                conn.close()

                return redirect(url_for("login"))

            except sqlite3.IntegrityError:
                conn.close()
                message = "This email is already registered."

    return render_template("signup.html", message=message)

@app.route("/login", methods=["GET", "POST"])
def login():
    message = ""

    if request.method == "POST":
        email = request.form["email"].strip().lower()
        password = request.form["password"]

        conn = sqlite3.connect(DATABASE)
        conn.row_factory = sqlite3.Row

        user = conn.execute(
            "SELECT * FROM users WHERE email = ?",
            (email,)
        ).fetchone()

        conn.close()

        if user and check_password_hash(user["password_hash"], password):
            session.clear()
            session["user_id"] = user["id"]
            session["user_name"] = user["name"]

            return redirect(url_for("home"))

        else:
            message = "Invalid email or password."

    return render_template("login.html", message=message)


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("home"))


@app.route("/toggle-favourite/<driver_slug>", methods=["POST"])
def toggle_favourite(driver_slug):

    if "user_id" not in session:
        return redirect(url_for("login"))

    selected_driver = next(
        (d for d in drivers if d["slug"] == driver_slug),
        None
    )

    if selected_driver is None:
        abort(404)

    conn = sqlite3.connect(DATABASE)

    existing = conn.execute(
        "SELECT id FROM favourites WHERE user_id = ? AND driver_slug = ?",
        (session["user_id"], driver_slug)
    ).fetchone()

    if existing:
        conn.execute(
            "DELETE FROM favourites WHERE user_id = ? AND driver_slug = ?",
            (session["user_id"], driver_slug)
        )
    else:
        conn.execute(
            "INSERT INTO favourites (user_id, driver_slug) VALUES (?, ?)",
            (session["user_id"], driver_slug)
        )

    conn.commit()
    conn.close()

    return_to = request.form.get("next", "/drivers")

    if not return_to.startswith("/") or return_to.startswith("//"):
        return_to = url_for("show_drivers")

    return redirect(return_to)


@app.route("/favourites")
def show_favourites():

    if "user_id" not in session:
        return redirect(url_for("login"))

    conn = sqlite3.connect(DATABASE)

    saved = conn.execute(
        "SELECT driver_slug FROM favourites WHERE user_id = ?",
        (session["user_id"],)
    ).fetchall()

    conn.close()

    favourite_slugs = {row[0] for row in saved}

    favourite_drivers = [
        driver for driver in drivers
        if driver["slug"] in favourite_slugs
    ]

    return render_template(
        "favourites.html",
        favourite_drivers=favourite_drivers
    )


# ---------------- DRIVERS ----------------


drivers = [

    {
        "name": "George Russell",
        "team": "Mercedes",
        "country": "United Kingdom",
        "number": "63",
        "slug": "george-russell",
        "bio": "George Russell is a British racing driver known for his consistency, precision and strong qualifying performances. He joined Mercedes in 2022 after establishing himself at Williams.",
        "debut": "2019",
        "previous_teams": ["Williams"],
        "starts": 172,
        "wins": 8,
        "podiums": 32,
        "titles": 0,
        "highlight": "Won his first Formula 1 Grand Prix at the 2022 São Paulo Grand Prix."
    },

    {
        "name": "Kimi Antonelli",
        "team": "Mercedes",
        "country": "Italy",
        "number": "12",
        "slug": "kimi-antonelli",
        "bio": "Andrea Kimi Antonelli is an Italian racing driver who progressed rapidly through junior motorsport. Mercedes promoted him to Formula 1 in 2025, making him one of the youngest drivers on the grid.",
        "debut": "2025",
        "previous_teams": [],
        "starts": 44,
        "wins": 9,
        "podiums": 19,
        "titles": 1,
        "highlight": "Became a Formula 1 race winner and World Champion in the 2026 season."
    },

    {
        "name": "Charles Leclerc",
        "team": "Ferrari",
        "country": "Monaco",
        "number": "16",
        "slug": "charles-leclerc",
        "bio": "Charles Leclerc is a Monegasque racing driver who joined Ferrari in 2019. He is particularly recognised for his speed in qualifying and his ability to compete at the front of the grid.",
        "debut": "2018",
        "previous_teams": ["Sauber"],
        "starts": 191,
        "wins": 9,
        "podiums": 56,
        "titles": 0,
        "highlight": "Won his home race, the Monaco Grand Prix, in 2024."
    },

    {
        "name": "Lewis Hamilton",
        "team": "Ferrari",
        "country": "United Kingdom",
        "number": "44",
        "slug": "lewis-hamilton",
        "bio": "Lewis Hamilton is a British racing driver widely regarded as one of Formula 1's most successful competitors. He won multiple championships with Mercedes before moving to Ferrari in 2025.",
        "debut": "2007",
        "previous_teams": ["McLaren", "Mercedes"],
        "starts": 400,
        "wins": 106,
        "podiums": 209,
        "titles": 7,
        "highlight": "Shares the record for the most Formula 1 World Championships, with seven titles."
    },

    {
        "name": "Max Verstappen",
        "team": "Red Bull Racing",
        "country": "Netherlands",
        "number": "3",
        "slug": "max-verstappen",
        "bio": "Max Verstappen is a Dutch racing driver known for his aggressive racing style and exceptional speed. He became the youngest driver to compete in Formula 1 and has won four consecutive championships from 2021 to 2024.",
        "debut": "2015",
        "previous_teams": ["Toro Rosso"],
        "starts": 253,
        "wins": 74,
        "podiums": 139,
        "titles": 4,
        "highlight": "Became the youngest Grand Prix winner at the 2016 Spanish Grand Prix."
    },

    {
        "name": "Isack Hadjar",
        "team": "Red Bull Racing",
        "country": "France",
        "number": "6",
        "slug": "isack-hadjar",
        "bio": "Isack Hadjar is a French racing driver who made his Formula 1 debut in 2025. After progressing through the junior categories, he earned a promotion to Red Bull Racing for 2026.",
        "debut": "2025",
        "previous_teams": ["Racing Bulls"],
        "starts": 41,
        "wins": 0,
        "podiums": 4,
        "titles": 0,
        "highlight": "Secured his maiden Formula 1 podium at the 2025 Dutch Grand Prix."
    },

    {
        "name": "Lando Norris",
        "team": "McLaren",
        "country": "United Kingdom",
        "number": "1",
        "slug": "lando-norris",
        "bio": "Lando Norris is a British racing driver who has been part of McLaren since his Formula 1 debut. Known for his speed and competitive nature, he won his first World Championship in 2025.",
        "debut": "2019",
        "previous_teams": [],
        "starts": 171,
        "wins": 14,
        "podiums": 50,
        "titles": 1,
        "highlight": "Won the 2025 Formula 1 World Drivers' Championship."
    },

    {
        "name": "Oscar Piastri",
        "team": "McLaren",
        "country": "Australia",
        "number": "81",
        "slug": "oscar-piastri",
        "bio": "Oscar Piastri is an Australian racing driver who joined McLaren in 2023. Before entering Formula 1, he achieved championship victories in both Formula 3 and Formula 2.",
        "debut": "2023",
        "previous_teams": [],
        "starts": 88,
        "wins": 9,
        "podiums": 28,
        "titles": 0,
        "highlight": "Won his first Formula 1 Grand Prix at the 2024 Hungarian Grand Prix."
    },

    {
        "name": "Liam Lawson",
        "team": "Racing Bulls",
        "country": "New Zealand",
        "number": "30",
        "slug": "liam-lawson",
        "bio": "Liam Lawson is a New Zealand racing driver who progressed through the Red Bull junior programme. He made his Formula 1 debut as a substitute driver in 2023 before earning a full-time seat.",
        "debut": "2023",
        "previous_teams": ["AlphaTauri", "Red Bull Racing"],
        "starts": 55,
        "wins": 0,
        "podiums": 0,
        "titles": 0,
        "highlight": "Impressed during his substitute appearances before securing a full-time F1 opportunity."
    },

    {
        "name": "Arvid Lindblad",
        "team": "Racing Bulls",
        "country": "United Kingdom",
        "number": "41",
        "slug": "arvid-lindblad",
        "bio": "Arvid Lindblad is a British racing driver and member of the Red Bull Junior Team. He progressed through Formula 3 and Formula 2 before making his Formula 1 debut in 2026.",
        "debut": "2026",
        "previous_teams": [],
        "starts": 19,
        "wins": 0,
        "podiums": 0,
        "titles": 0,
        "highlight": "Became the youngest race winner in Formula 2 history in 2025."
    },

    {
        "name": "Pierre Gasly",
        "team": "Alpine",
        "country": "France",
        "number": "10",
        "slug": "pierre-gasly",
        "bio": "Pierre Gasly is a French racing driver who has competed for several Formula 1 teams. He is known for his determination and achieved a memorable first Grand Prix victory in 2020.",
        "debut": "2017",
        "previous_teams": ["Toro Rosso", "Red Bull Racing", "AlphaTauri"],
        "starts": 197,
        "wins": 1,
        "podiums": 5,
        "titles": 0,
        "highlight": "Won the 2020 Italian Grand Prix at Monza."
    },

    {
        "name": "Franco Colapinto",
        "team": "Alpine",
        "country": "Argentina",
        "number": "43",
        "slug": "franco-colapinto",
        "bio": "Franco Colapinto is an Argentinian racing driver who entered Formula 1 in 2024. He progressed through the Williams Driver Academy before joining Alpine.",
        "debut": "2024",
        "previous_teams": ["Williams"],
        "starts": 46,
        "wins": 0,
        "podiums": 0,
        "titles": 0,
        "highlight": "Scored points during his rookie Formula 1 season with Williams."
    },

    {
        "name": "Oliver Bearman",
        "team": "Haas F1 Team",
        "country": "United Kingdom",
        "number": "87",
        "slug": "oliver-bearman",
        "bio": "Oliver Bearman is a British racing driver who made his Formula 1 debut with Ferrari in 2024. His impressive substitute performances earned him a full-time seat with Haas in 2025.",
        "debut": "2024",
        "previous_teams": ["Ferrari (substitute appearances)"],
        "starts": 47,
        "wins": 0,
        "podiums": 0,
        "titles": 0,
        "highlight": "Scored points on his Formula 1 debut with Ferrari at the 2024 Saudi Arabian Grand Prix."
    },
        
{
    "name": "Esteban Ocon",
    "team": "Haas F1 Team",
    "country": "France",
    "number": "31",
    "slug": "esteban-ocon",
    "bio": "Esteban Ocon is a French racing driver who made his Formula 1 debut in 2016 with Manor Racing. After competing for Force India, Renault and Alpine, he joined Haas in 2025. He is known for his determination and strong wheel-to-wheel racing.",
    "debut": "2016",
    "previous_teams": ["Manor","Force India / Racing Point","Renault","Alpine" ],
    "starts": 198,
    "wins": 1,
    "podiums": 4,
    "titles": 0,
    "highlight": "Won his first Formula 1 Grand Prix at the 2021 Hungarian Grand Prix, securing Alpine's first victory as a constructor."
},

    {
        "name": "Nico Hulkenberg",
        "team": "Audi",
        "country": "Germany",
        "number": "27",
        "slug": "nico-hulkenberg",
        "bio": "Nico Hulkenberg is a German racing driver known for his experience and consistency. After competing for several teams, he joined Sauber in 2025 ahead of its transition into Audi.",
        "debut": "2010",
        "previous_teams": ["Williams", "Force India", "Sauber", "Renault", "Haas"],
        "starts": 269,
        "wins": 0,
        "podiums": 1,
        "titles": 0,
        "highlight": "Achieved his first Formula 1 podium at the 2025 British Grand Prix."
    },

    {
        "name": "Gabriel Bortoleto",
        "team": "Audi",
        "country": "Brazil",
        "number": "5",
        "slug": "gabriel-bortoleto",
        "bio": "Gabriel Bortoleto is a Brazilian racing driver who won both the Formula 3 and Formula 2 championships before entering Formula 1. He made his debut with Sauber in 2025.",
        "debut": "2025",
        "previous_teams": ["Sauber"],
        "starts": 43,
        "wins": 0,
        "podiums": 0,
        "titles": 0,
        "highlight": "Won the Formula 2 championship in 2024 before graduating to Formula 1."
    },

    {
        "name": "Carlos Sainz",
        "team": "Williams",
        "country": "Spain",
        "number": "55",
        "slug": "carlos-sainz",
        "bio": "Carlos Sainz is a Spanish racing driver who has competed for several major Formula 1 teams. He is known for his technical feedback, consistency and racecraft.",
        "debut": "2015",
        "previous_teams": ["Toro Rosso", "Renault", "McLaren", "Ferrari"],
        "starts": 249,
        "wins": 4,
        "podiums": 29,
        "titles": 0,
        "highlight": "Secured four Grand Prix victories before joining Williams in 2025."
    },

    {
        "name": "Alexander Albon",
        "team": "Williams",
        "country": "Thailand",
        "number": "23",
        "slug": "alexander-albon",
        "bio": "Alexander Albon is a Thai-British racing driver who made his Formula 1 debut in 2019. After racing for Toro Rosso and Red Bull, he joined Williams in 2022.",
        "debut": "2019",
        "previous_teams": ["Toro Rosso", "Red Bull Racing"],
        "starts": 147,
        "wins": 0,
        "podiums": 2,
        "titles": 0,
        "highlight": "Achieved two podium finishes during his time with Red Bull Racing."
    },

    {
        "name": "Fernando Alonso",
        "team": "Aston Martin",
        "country": "Spain",
        "number": "14",
        "slug": "fernando-alonso",
        "bio": "Fernando Alonso is a Spanish racing driver and two-time Formula 1 World Champion. Known for his racecraft and longevity, he has competed across multiple eras of Formula 1.",
        "debut": "2001",
        "previous_teams": ["Minardi", "Renault", "McLaren", "Ferrari", "Alpine"],
        "starts": 446,
        "wins": 32,
        "podiums": 106,
        "titles": 2,
        "highlight": "Won consecutive Formula 1 World Championships in 2005 and 2006."
    },

    {
        "name": "Lance Stroll",
        "team": "Aston Martin",
        "country": "Canada",
        "number": "18",
        "slug": "lance-stroll",
        "bio": "Lance Stroll is a Canadian racing driver who entered Formula 1 in 2017. He has raced for Williams and Racing Point before continuing with the team under the Aston Martin name.",
        "debut": "2017",
        "previous_teams": ["Williams", "Racing Point"],
        "starts": 209,
        "wins": 0,
        "podiums": 3,
        "titles": 0,
        "highlight": "Achieved his first Formula 1 podium at the 2017 Azerbaijan Grand Prix."
    },

    {
        "name": "Sergio Perez",
        "team": "Cadillac",
        "country": "Mexico",
        "number": "11",
        "slug": "sergio-perez",
        "bio": "Sergio Perez is a Mexican racing driver known for his tyre management and strong defensive driving. He has competed for several teams, including Red Bull, before joining Cadillac in 2026.",
        "debut": "2011",
        "previous_teams": ["Sauber", "McLaren", "Force India", "Racing Point", "Red Bull Racing"],
        "starts": 301,
        "wins": 6,
        "podiums": 39,
        "titles": 0,
        "highlight": "Won the 2020 Sakhir Grand Prix and helped Red Bull secure Constructors' Championships."
    },

    {
        "name": "Valtteri Bottas",
        "team": "Cadillac",
        "country": "Finland",
        "number": "77",
        "slug": "valtteri-bottas",
        "bio": "Valtteri Bottas is a Finnish racing driver who built a successful career with Williams and Mercedes. He has ten Grand Prix victories and returned to the grid with Cadillac in 2026.",
        "debut": "2013",
        "previous_teams": ["Williams", "Mercedes", "Alfa Romeo", "Kick Sauber"],
        "starts": 265,
        "wins": 10,
        "podiums": 67,
        "titles": 0,
        "highlight": "Finished runner-up in the Drivers' Championship in 2019 and 2020."
    }

]


# ---------------- TEAMS ----------------

teams = [
    {"name": "McLaren", "detail": "Lando Norris and Oscar Piastri"},
    {"name": "Mercedes", "detail": "George Russell and Kimi Antonelli"},
    {"name": "Red Bull Racing", "detail": "Max Verstappen and Isack Hadjar"},
    {"name": "Ferrari", "detail": "Charles Leclerc and Lewis Hamilton"},
    {"name": "Williams", "detail": "Carlos Sainz and Alexander Albon"},
    {"name": "Racing Bulls", "detail": "Liam Lawson and Arvid Lindblad"},
    {"name": "Aston Martin", "detail": "Fernando Alonso and Lance Stroll"},
    {"name": "Haas F1 Team", "detail": "Oliver Bearman and Esteban Ocon"},
    {"name": "Audi", "detail": "Nico Hulkenberg and Gabriel Bortoleto"},
    {"name": "Alpine", "detail": "Pierre Gasly and Franco Colapinto"},
    {"name": "Cadillac", "detail": "Sergio Perez and Valtteri Bottas"}
]


# ---------------- CIRCUITS ----------------

circuits = [
    {"name": "Australian Grand Prix", "detail": "Melbourne, Australia | Albert Park"},
    {"name": "Chinese Grand Prix", "detail": "Shanghai, China | Shanghai International Circuit"},
    {"name": "Japanese Grand Prix", "detail": "Suzuka, Japan | Suzuka Circuit"},
    {"name": "Miami Grand Prix", "detail": "Miami, USA | Miami International Autodrome"},
    {"name": "Canadian Grand Prix", "detail": "Montreal, Canada | Circuit Gilles-Villeneuve"},
    {"name": "Monaco Grand Prix", "detail": "Monte Carlo, Monaco | Circuit de Monaco"},
    {"name": "Spanish Grand Prix", "detail": "Barcelona, Spain | Circuit de Barcelona-Catalunya"},
    {"name": "Austrian Grand Prix", "detail": "Spielberg, Austria | Red Bull Ring"},
    {"name": "British Grand Prix", "detail": "Silverstone, UK | Silverstone Circuit"},
    {"name": "Belgian Grand Prix", "detail": "Stavelot, Belgium | Spa-Francorchamps"},
    {"name": "Hungarian Grand Prix", "detail": "Budapest, Hungary | Hungaroring"},
    {"name": "Dutch Grand Prix", "detail": "Zandvoort, Netherlands | Circuit Zandvoort"},
    {"name": "Italian Grand Prix", "detail": "Monza, Italy | Autodromo Nazionale Monza"},
    {"name": "Spanish Grand Prix - Madrid", "detail": "Madrid, Spain | Madring"},
    {"name": "Azerbaijan Grand Prix", "detail": "Baku, Azerbaijan | Baku City Circuit"},
    {"name": "Bahrain Grand Prix", "detail": "Sakhir, Bahrain | Bahrain International Circuit"},
    {"name": "Singapore Grand Prix", "detail": "Singapore | Marina Bay Street Circuit"},
    {"name": "United States Grand Prix", "detail": "Austin, USA | Circuit of The Americas"},
    {"name": "Mexico City Grand Prix", "detail": "Mexico City, Mexico | Autódromo Hermanos Rodríguez"},
    {"name": "São Paulo Grand Prix", "detail": "São Paulo, Brazil | Interlagos"},
    {"name": "Las Vegas Grand Prix", "detail": "Las Vegas, USA | Las Vegas Strip Circuit"},
    {"name": "Qatar Grand Prix", "detail": "Lusail, Qatar | Lusail International Circuit"},
    {"name": "Abu Dhabi Grand Prix", "detail": "Abu Dhabi, UAE | Yas Marina Circuit"}
]


# ---------------- WEBSITE ROUTES ----------------

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/drivers")
def show_drivers():

    search_query = request.args.get("search", "").strip().lower()

    filtered_drivers = []

    for driver in drivers:
        if (
            search_query in driver["name"].lower()
            or search_query in driver["team"].lower()
            or search_query in driver["country"].lower()
        ):
            filtered_drivers.append(driver)

    return render_template(
        "drivers.html",
        drivers=filtered_drivers,
        search_query=search_query
    )


# INDIVIDUAL DRIVER PROFILE

@app.route("/driver/<driver_slug>")
def driver_profile(driver_slug):

    selected_driver = next(
        (driver for driver in drivers if driver["slug"] == driver_slug),
        None
    )

    if selected_driver is None:
        abort(404)

    return render_template(
        "driver.html",
        driver=selected_driver
    )


@app.route("/teams")
def show_teams():
    return render_template(
        "explore.html",
        page_title="F1 TEAMS",
        subtitle="THE TEAMS BEHIND THE MACHINES",
        items=teams
    )


@app.route("/circuits")
def show_circuits():
    return render_template(
        "explore.html",
        page_title="F1 CIRCUITS",
        subtitle="EXPLORE THE 2026 RACE CALENDAR",
        items=circuits
    )


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
