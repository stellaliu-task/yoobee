from database import Database
import os

def get_image_bytes(filename):
    with open(filename, "rb") as f:
        return f.read()

def main():
    db = Database()
    try:
        # --- USERS ---
        db.conn.execute(
            "INSERT OR IGNORE INTO users (username, email, password_hash) VALUES (?, ?, ?)",
            ("testuser", "testuser@mail.com", "hash1234")
        )
        user_id = db.conn.execute(
            "SELECT id FROM users WHERE username=?", ("testuser",)
        ).fetchone()[0]

        # --- ADMINS ---
        db.conn.execute(
            "INSERT OR IGNORE INTO admins (name, email, password_hash) VALUES (?, ?, ?)",
            ("admin", "admin@mail.com", "adminhash")
        )
        admin_id = db.conn.execute(
            "SELECT id FROM admins WHERE email=?", ("admin@mail.com",)
        ).fetchone()[0]

        # --- TAGS ---
        tag_list = [
            "Māori Literature", "Crime", "Scottish", "Nonfiction", "Classic"
        ]
        for tag in tag_list:
            db.conn.execute(
                "INSERT OR IGNORE INTO tags (name) VALUES (?)", (tag,)
            )

        tag_ids = {tag: db.conn.execute(
            "SELECT id FROM tags WHERE name=?", (tag,)
        ).fetchone()[0] for tag in tag_list}

        # --- BOOKS ---
        book_data = [
            {
                "title": "Before Maori",
                "author": "Ross M Bodle",
                "description": "Explores evidence of pre-Maori inhabitation in NZ, migration, language, and cultural links across the Pacific.",
                "catalog": "History",
                "status": "want_to_read",
                "tags": ["Māori Literature"],
                "cover_img": "covers/Before Maori.png"
            },
            {
                "title": "Bloody January",
                "author": "Alan Parks",
                "description": "Detective Harry McCoy investigates a deadly Glasgow shooting, uncovering secrets of the city’s elite.",
                "catalog": "Fiction",
                "status": "want_to_read",
                "tags": ["Crime", "Scottish"],
                "cover_img": "covers/Bloody January.png"
            },
            {
                "title": "Māori Language",
                "author": "Urban Napflin",
                "description": "Short course for travelers/newcomers to learn basic Te Reo Maori and culture.",
                "catalog": "Language",
                "status": "want_to_read",
                "tags": ["Māori Literature"],
                "cover_img": "covers/Māori Language.png"
            },
            {
                "title": "Maori Music",
                "author": "Mervyn McLean",
                "description": "Best introduction to Maori music—fieldwork, songs, performance, and eyewitness accounts. Classic reference.",
                "catalog": "Music",
                "status": "want_to_read",
                "tags": ["Māori Literature"],
                "cover_img": "covers/Maori Music.png"
            },
            {
                "title": "Maori Times, Maori Places",
                "author": "Karen Sinclair",
                "description": "A compilation of twenty-five years of fieldwork with a group of Maori. Examines oral histories, pilgrimages, gender, colonialism, and the complexities of Maori identity.",
                "catalog": "History",
                "status": "want_to_read",
                "tags": ["Māori Literature"],
                "cover_img": "covers/Maori Times.png"
            },
            {
                "title": "Māori Warriors",
                "author": "Ray McClellan",
                "description": "Covers haka, peruperu, weapons, and war traditions—stories of bravery, ritual, and battle in Maori history.",
                "catalog": "History",
                "status": "want_to_read",
                "tags": ["Māori Literature"],
                "cover_img": "covers/Māori Warriors.png"
            },
            {
                "title": "Maori",
                "author": "Leslie Strudwick",
                "description": "The Maori often greet each other with the hongi, in which two people press their noses together to exchange the ha, or breath of life. The Maori live in New Zealand. Find out more about this rich world culture in Maori. This is an AV2 media-enhanced book.",
                "catalog": "Culture",
                "status": "want_to_read",
                "tags": ["Māori Literature"],
                "cover_img": "covers/Maori.png"
            },
            {
                "title": "Stolen Lives: the Untold Stories of the Lawson Quins",
                "author": "Paul Little",
                "description": "The tragic, true story of the Lawson Quins—miracle siblings, childhood trauma, survival, and hope.",
                "catalog": "Biography",
                "status": "want_to_read",
                "tags": ["Nonfiction"],
                "cover_img": "covers/Stolen Lives.png"
            },
            {
                "title": "The Tenant of Wildfell Hall",
                "author": "Anne Brontë",
                "description": "Classic novel—Gilbert Markham meets the mysterious widow of Wildfell Hall in this Victorian story of rumors, secrets, and resilience.",
                "catalog": "Fiction",
                "status": "want_to_read",
                "tags": ["Classic"],
                "cover_img": "covers/The Tenant.png"
            },
            {
                "title": "Tikanga Maori",
                "author": "Hirini Moko Mead",
                "description": "A comprehensive survey of tikanga Maori (Maori custom), ranging from the everyday to the esoteric, with authoritative commentary.",
                "catalog": "Culture",
                "status": "want_to_read",
                "tags": ["Māori Literature"],
                "cover_img": "covers/Tikanga Maori.png"
            },
        ]

        book_ids = []
        for book in book_data:
            cover_bytes = get_image_bytes(book["cover_img"])
            db.conn.execute("""
                INSERT INTO books (user_id, title, author, description, catalog, cover_picture, status)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (user_id, book["title"], book["author"], book["description"], book["catalog"], cover_bytes, book["status"]))
            book_id = db.conn.execute("SELECT last_insert_rowid()").fetchone()[0]
            book_ids.append(book_id)
            for tag in book["tags"]:
                db.conn.execute(
                    "INSERT OR IGNORE INTO book_tags (book_id, tag_id) VALUES (?, ?)",
                    (book_id, tag_ids[tag])
                )

        # --- ACTIVITIES ---
        for book_id in book_ids:
            db.conn.execute("""
                INSERT INTO activities (user_id, book_id, action, message)
                VALUES (?, ?, ?, ?)
            """, (user_id, book_id, "added_book", "Added new book"))

        activity_ids = [row[0] for row in db.conn.execute("SELECT id FROM activities WHERE user_id=?", (user_id,)).fetchall()]

        # --- LIKES (testuser likes their first 3 activities) ---
        for activity_id in activity_ids[:3]:
            db.conn.execute("""
                INSERT OR IGNORE INTO likes (user_id, activity_id)
                VALUES (?, ?)
            """, (user_id, activity_id))

        # --- REVIEWS (testuser reviews first 2 books) ---
        for idx, activity_id in enumerate(activity_ids[:2]):
            db.conn.execute("""
                INSERT INTO reviews (user_id, activity_id, content)
                VALUES (?, ?, ?)
            """, (user_id, activity_id, f"This is a review for activity {activity_id}."))

        # --- THEMES (one theme and assign first 2 books) ---
        db.conn.execute("""
            INSERT INTO themes (title, is_hidden) VALUES (?, 0)
        """, ("Best of Māori Literature",))
        theme_id = db.conn.execute("SELECT last_insert_rowid()").fetchone()[0]
        for book_id in book_ids[:2]:
            db.conn.execute("""
                INSERT OR IGNORE INTO theme_books (theme_id, book_id)
                VALUES (?, ?)
            """, (theme_id, book_id))

        db.conn.commit()
        print("Test data inserted for all tables.")

    except Exception as e:
        print(f"Error in main(): {e}")
    finally:
        db.close()

if __name__ == "__main__":
    main()
