from flask import Flask, request, jsonify, session
import sqlite3
from flask_cors import CORS

from admin_manager import AdminManager
from books_manager import BooksManager
from user_manager import UserManager
from likes_manager import LikesManager
from review_manager import ReviewManager

app = Flask(__name__)
CORS(app)
app.secret_key = "^GKIOJFHIJPKTK::JL12"

def get_db():
    conn = sqlite3.connect('bookhive.db')
    conn.row_factory = sqlite3.Row
    return conn

# Instantiate managers with new db connection per request
def managers():
    db = get_db()
    return (
        AdminManager(db),
        BooksManager(db),
        UserManager(db),
        LikesManager(db),
        ReviewManager(db)
    )

# ---------- USER AUTH ----------

@app.route("/register", methods=["POST"])
def register():
    _, _, user_manager, _, _ = managers()
    data = request.get_json()
    user_id = user_manager.register_user(data["username"], data["email"], data["password"])
    if user_id:
        session["user_id"] = user_id
        return jsonify({"success": True, "user_id": user_id})
    else:
        return jsonify({"success": False, "error": "Username or email already in use"}), 400

@app.route("/login", methods=["POST"])
def login():
    _, _, user_manager, _, _ = managers()
    data = request.get_json()
    user_id = user_manager.authenticate_user(data["username_or_email"], data["password"])
    if user_id:
        session["user_id"] = user_id
        return jsonify({"success": True, "user_id": user_id})
    else:
        return jsonify({"success": False, "error": "Invalid credentials"}), 401

@app.route("/logout", methods=["POST"])
def logout():
    session.clear()
    return jsonify({"success": True})

# ---------- BOOKS ----------

@app.route("/books", methods=["POST"])
def add_book():
    _, books_manager, _, _, _ = managers()
    user_id = session.get("user_id")
    if not user_id:
        return jsonify({"success": False, "error": "Unauthorized"}), 401
    data = request.get_json()
    book_id = books_manager.add_book(
        user_id,
        data["title"],
        data.get("author", ""),
        data.get("description", ""),
        data.get("catalog", ""),
        data["status"],
        data.get("tags", [])
    )
    return jsonify({"success": True, "book_id": book_id})

@app.route("/books/<int:book_id>", methods=["PUT"])
def edit_book(book_id):
    _, books_manager, _, _, _ = managers()
    user_id = session.get("user_id")
    if not user_id:
        return jsonify({"success": False, "error": "Unauthorized"}), 401
    data = request.get_json()
    updated = books_manager.edit_book(
        book_id, user_id,
        data.get("title"), data.get("author"),
        data.get("description"), data.get("catalog"),
        data.get("status")
    )
    if updated:
        return jsonify({"success": True})
    else:
        return jsonify({"success": False, "error": "Not found"}), 404

@app.route("/books/<int:book_id>", methods=["DELETE"])
def hide_book(book_id):
    _, books_manager, _, _, _ = managers()
    user_id = session.get("user_id")
    if not user_id:
        return jsonify({"success": False, "error": "Unauthorized"}), 401
    deleted = books_manager.hide_book(book_id, user_id)
    if deleted:
        return jsonify({"success": True})
    else:
        return jsonify({"success": False, "error": "Not found"}), 404

@app.route("/books/<int:book_id>/restore", methods=["POST"])
def restore_book(book_id):
    _, books_manager, _, _, _ = managers()
    user_id = session.get("user_id")
    if not user_id:
        return jsonify({"success": False, "error": "Unauthorized"}), 401
    restored = books_manager.restore_book(book_id, user_id)
    if restored:
        return jsonify({"success": True})
    else:
        return jsonify({"success": False, "error": "Not found"}), 404

@app.route("/users/<int:user_id>/books", methods=["GET"])
def list_books(user_id):
    _, books_manager, _, _, _ = managers()
    # Ownership check
    if session.get("user_id") != user_id:
        return jsonify({"success": False, "error": "Unauthorized"}), 401
    status = request.args.get("status")
    tag = request.args.get("tag")
    catalog = request.args.get("catalog")
    books = books_manager.get_books_by_user(user_id, status=status, tag=tag, catalog=catalog)
    result = []
    for b in books:
        # Convert sqlite3.Row to dict if needed
        book_dict = dict(b)
        book_dict["tags"] = book_dict.get("tags", "").split(",") if book_dict.get("tags") else []
        result.append(book_dict)
    return jsonify(result)

@app.route("/books/<int:book_id>", methods=["GET"])
def get_book(book_id):
    _, books_manager, _, _, _ = managers()
    user_id = session.get("user_id")
    book = books_manager.get_book_by_id(book_id, user_id)
    if not book:
        return jsonify(None)
    book_row, tags = book
    book_dict = dict(book_row)
    book_dict["tags"] = tags
    return jsonify(book_dict)

@app.route("/books/<int:book_id>/tags", methods=["POST"])
def add_tag_to_book(book_id):
    _, books_manager, _, _, _ = managers()
    user_id = session.get("user_id")
    tag = request.get_json().get("tag")
    if not tag:
        return jsonify({"success": False, "error": "Tag required"}), 400
    success = books_manager.add_tag_to_book(book_id, user_id, tag)
    return jsonify({"success": success})

@app.route("/books/<int:book_id>/tags/<tag>", methods=["DELETE"])
def remove_tag_from_book(book_id, tag):
    _, books_manager, _, _, _ = managers()
    user_id = session.get("user_id")
    success = books_manager.remove_tag_from_book(book_id, user_id, tag)
    return jsonify({"success": success})

@app.route("/books/<int:book_id>/tags", methods=["GET"])
def get_tags_for_book(book_id):
    _, books_manager, _, _, _ = managers()
    user_id = session.get("user_id")
    tags = books_manager.get_tags_for_book(book_id, user_id)
    return jsonify(tags)

# ---------- LIKES ----------

@app.route("/likes/<int:activity_id>", methods=["POST"])
def add_like(activity_id):
    _, _, _, likes_manager, _ = managers()
    user_id = session.get("user_id")
    if not user_id:
        return jsonify({"success": False, "error": "Unauthorized"}), 401
    added = likes_manager.add_like(user_id, activity_id)
    if added:
        return jsonify({"success": True})
    else:
        return jsonify({"success": False, "error": "Already liked"}), 400

@app.route("/likes/<int:activity_id>", methods=["DELETE"])
def remove_like(activity_id):
    _, _, _, likes_manager, _ = managers()
    user_id = session.get("user_id")
    if not user_id:
        return jsonify({"success": False, "error": "Unauthorized"}), 401
    removed = likes_manager.remove_like(user_id, activity_id)
    if removed:
        return jsonify({"success": True})
    else:
        return jsonify({"success": False, "error": "Like not found"}), 404

@app.route("/activities/<int:activity_id>/likes", methods=["GET"])
def get_activity_likes(activity_id):
    _, _, _, likes_manager, _ = managers()
    likes = likes_manager.get_likes_for_activity(activity_id)
    result = []
    for l in likes:
        result.append(dict(l))
    return jsonify(result)

@app.route("/activities/<int:activity_id>/like_count", methods=["GET"])
def get_like_count(activity_id):
    _, _, _, likes_manager, _ = managers()
    count = likes_manager.count_likes(activity_id)
    return jsonify({"activity_id": activity_id, "like_count": count})

@app.route("/users/<int:user_id>/likes", methods=["GET"])
def get_user_likes(user_id):
    _, _, _, likes_manager, _ = managers()
    if session.get("user_id") != user_id:
        return jsonify({"success": False, "error": "Unauthorized"}), 401
    activities = likes_manager.get_liked_activities_by_user(user_id)
    return jsonify([{"activity_id": aid} for aid in activities])

# ---------- REVIEWS / REPLIES ----------

@app.route("/activities/<int:activity_id>/replies", methods=["POST"])
def add_reply(activity_id):
    _, _, _, _, review_manager = managers()
    user_id = session.get("user_id")
    if not user_id:
        return jsonify({"success": False, "error": "Unauthorized"}), 401
    content = request.get_json().get("content", "")
    reply_id = review_manager.add_reply(user_id, activity_id, content)
    if reply_id:
        return jsonify({"success": True, "reply_id": reply_id})
    else:
        return jsonify({"success": False, "error": "Content cannot be blank"}), 400

@app.route("/activities/<int:activity_id>/replies", methods=["GET"])
def get_replies_for_activity(activity_id):
    _, _, _, _, review_manager = managers()
    replies = review_manager.get_replies_for_activity(activity_id)
    return jsonify([dict(r) for r in replies])

@app.route("/replies/<int:reply_id>", methods=["PUT"])
def edit_reply(reply_id):
    _, _, _, _, review_manager = managers()
    user_id = session.get("user_id")
    content = request.get_json().get("content", "")
    success = review_manager.edit_reply(reply_id, user_id, content)
    return jsonify({"success": success})

@app.route("/replies/<int:reply_id>", methods=["DELETE"])
def hide_reply(reply_id):
    _, _, _, _, review_manager = managers()
    user_id = session.get("user_id")
    success = review_manager.hide_reply(reply_id, user_id)
    return jsonify({"success": success})

@app.route("/replies/<int:reply_id>/restore", methods=["POST"])
def restore_reply(reply_id):
    _, _, _, _, review_manager = managers()
    user_id = session.get("user_id")
    success = review_manager.restore_reply(reply_id, user_id)
    return jsonify({"success": success})

@app.route("/replies/<int:reply_id>", methods=["GET"])
def get_reply(reply_id):
    _, _, _, _, review_manager = managers()
    reply = review_manager.get_reply_by_id(reply_id)
    return jsonify(dict(reply) if reply else None)

# ---------- USER PROFILE ----------

@app.route("/users/<int:user_id>", methods=["GET"])
def get_user_profile(user_id):
    _, _, user_manager, _, _ = managers()
    if session.get("user_id") != user_id:
        return jsonify({"success": False, "error": "Unauthorized"}), 401
    user = user_manager.get_user_by_id(user_id)
    return jsonify(dict(user) if user else None)

@app.route("/users/<int:user_id>", methods=["PUT"])
def update_user_profile(user_id):
    _, _, user_manager, _, _ = managers()
    if session.get("user_id") != user_id:
        return jsonify({"success": False, "error": "Unauthorized"}), 401
    data = request.get_json()
    updated = user_manager.update_user(
        user_id,
        data.get("username"), data.get("email"), data.get("password")
    )
    return jsonify({"success": updated})

@app.route("/users/<int:user_id>", methods=["DELETE"])
def soft_delete_user(user_id):
    _, _, user_manager, _, _ = managers()
    if session.get("user_id") != user_id:
        return jsonify({"success": False, "error": "Unauthorized"}), 401
    deleted = user_manager.soft_delete_user(user_id)
    return jsonify({"success": deleted})

@app.route("/users/<int:user_id>/restore", methods=["POST"])
def restore_user(user_id):
    _, _, user_manager, _, _ = managers()
    if session.get("user_id") != user_id:
        return jsonify({"success": False, "error": "Unauthorized"}), 401
    restored = user_manager.restore_user(user_id)
    return jsonify({"success": restored})

if __name__ == "__main__":
    app.run(debug=True)
