from flask import Flask, request, jsonify, session
import sqlite3
from flask_cors import CORS
import os

from admin_manager import AdminManager
from books_manager import BooksManager
from user_manager import UserManager
from likes_manager import LikesManager
from review_manager import ReviewManager

app = Flask(__name__)
CORS(app, resources={
    r"/api/*": {
        "origins": ["http://localhost:*", "http://127.0.0.1:*"],
        "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        "allow_headers": ["Content-Type", "Authorization"],
        "supports_credentials": True
    }
})
app.secret_key = "^GKIOJFHIJPKTK::JL12"

def get_db():
    
    print("Current working directory:", os.getcwd())
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    DB_PATH = os.path.join(BASE_DIR, 'bookhive.db')
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

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

@app.route("/api/register", methods=["POST", "OPTIONS"])
def register():
    if request.method == "OPTIONS":
        return '', 204
    _, _, user_manager, _, _ = managers()
    data = request.get_json()
    
    if not data or 'username' not in data or 'email' not in data or 'password' not in data:
        return jsonify({
            "success": False, 
            "error": "Missing required fields"
        }), 400
        
    try:
        user_id = user_manager.register_user(data["username"], data["email"], data["password"])
        if user_id:
            session["user_id"] = user_id
            return jsonify({
                "success": True, 
                "user_id": user_id
            })
        else:
            return jsonify({
                "success": False, 
                "error": "Username or email already in use"
            }), 400
    except Exception as e:
        return jsonify({
            "success": False, 
            "error": str(e)
        }), 500
    
@app.route("/api/users/me", methods=["GET"])
def get_current_user():
    user_id = session.get("user_id")
    if not user_id:
        return jsonify(None)
    
    _, _, user_manager, _, _ = managers()
    user = user_manager.get_user_by_id(user_id)
    if user:
        return jsonify(dict(user))
    return jsonify(None)

@app.route("/api/login", methods=["POST", "OPTIONS"])
def login():
    if request.method == "OPTIONS":
        return '', 204
    _, _, user_manager, _, _ = managers()
    data = request.get_json()
    # Accept either "username" or "email" as the username field
    username_or_email = data.get("username") or data.get("email")
    user_id = user_manager.authenticate_user(username_or_email, data["password"])
    if user_id:
        session["user_id"] = user_id
        return jsonify({"success": True, "user_id": user_id})
    else:
        return jsonify({"success": False, "error": "Invalid credentials"}), 401


@app.route("/api/logout", methods=["POST", "OPTIONS"])
def logout():
    if request.method == "OPTIONS":
        return '', 204
    session.clear()
    return jsonify({"success": True})

# ---------- BOOKS ----------

@app.route("/api/books", methods=["POST", "OPTIONS"])
def add_book():
    if request.method == "OPTIONS":
        return '', 204
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
        data.get("cover_picture", None),    # Add cover_picture if needed
        data["status"],
        data.get("tags", [])
    )
    return jsonify({"success": True, "book_id": book_id})

@app.route("/api/books/<int:book_id>", methods=["PUT", "OPTIONS"])
def edit_book(book_id):
    if request.method == "OPTIONS":
        return '', 204
    _, books_manager, _, _, _ = managers()
    user_id = session.get("user_id")
    if not user_id:
        return jsonify({"success": False, "error": "Unauthorized"}), 401
    data = request.get_json()
    updated = books_manager.edit_book(
        book_id, user_id,
        data.get("title"), data.get("author"),
        data.get("description"), data.get("catalog"),
        data.get("status"),
        data.get("cover_picture", None)   # Add cover_picture if needed
    )
    if updated:
        return jsonify({"success": True})
    else:
        return jsonify({"success": False, "error": "Not found"}), 404

@app.route("/api/books/<int:book_id>", methods=["DELETE", "OPTIONS"])
def hide_book(book_id):
    if request.method == "OPTIONS":
        return '', 204
    _, books_manager, _, _, _ = managers()
    user_id = session.get("user_id")
    if not user_id:
        return jsonify({"success": False, "error": "Unauthorized"}), 401
    deleted = books_manager.hide_book(book_id, user_id)
    if deleted:
        return jsonify({"success": True})
    else:
        return jsonify({"success": False, "error": "Not found"}), 404

@app.route("/api/books/<int:book_id>/restore", methods=["POST", "OPTIONS"])
def restore_book(book_id):
    if request.method == "OPTIONS":
        return '', 204
    _, books_manager, _, _, _ = managers()
    user_id = session.get("user_id")
    if not user_id:
        return jsonify({"success": False, "error": "Unauthorized"}), 401
    restored = books_manager.restore_book(book_id, user_id)
    if restored:
        return jsonify({"success": True})
    else:
        return jsonify({"success": False, "error": "Not found"}), 404

# GET endpoints for books don't need OPTIONS

@app.route("/api/users/<int:user_id>/books", methods=["GET"])
def list_books(user_id):
    _, books_manager, _, _, _ = managers()
    if session.get("user_id") != user_id:
        return jsonify({"success": False, "error": "Unauthorized"}), 401
    status = request.args.get("status")
    tag = request.args.get("tag")
    catalog = request.args.get("catalog")
    books = books_manager.get_books_by_user(user_id, status=status, tag=tag, catalog=catalog)
    result = []
    for b in books:
        book_dict = dict(b)
        book_dict["tags"] = book_dict.get("tags", "").split(",") if book_dict.get("tags") else []
        result.append(book_dict)
    return jsonify(result)

@app.route("/api/books/<int:book_id>", methods=["GET"])
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

@app.route("/api/books/<int:book_id>/tags", methods=["POST", "OPTIONS"])
def add_tag_to_book(book_id):
    if request.method == "OPTIONS":
        return '', 204
    _, books_manager, _, _, _ = managers()
    user_id = session.get("user_id")
    tag = request.get_json().get("tag")
    if not tag:
        return jsonify({"success": False, "error": "Tag required"}), 400
    success = books_manager.add_tag_to_book(book_id, user_id, tag)
    return jsonify({"success": success})

@app.route("/api/books/<int:book_id>/tags/<tag>", methods=["DELETE", "OPTIONS"])
def remove_tag_from_book(book_id, tag):
    if request.method == "OPTIONS":
        return '', 204
    _, books_manager, _, _, _ = managers()
    user_id = session.get("user_id")
    success = books_manager.remove_tag_from_book(book_id, user_id, tag)
    return jsonify({"success": success})

@app.route("/api/books/<int:book_id>/tags", methods=["GET"])
def get_tags_for_book(book_id):
    _, books_manager, _, _, _ = managers()
    user_id = session.get("user_id")
    tags = books_manager.get_tags_for_book(book_id, user_id)
    return jsonify(tags)

# ---------- LIKES ----------

@app.route("/api/likes/<int:activity_id>", methods=["POST", "OPTIONS"])
def add_like(activity_id):
    if request.method == "OPTIONS":
        return '', 204
    _, _, _, likes_manager, _ = managers()
    user_id = session.get("user_id")
    if not user_id:
        return jsonify({"success": False, "error": "Unauthorized"}), 401
    added = likes_manager.add_like(user_id, activity_id)
    if added:
        return jsonify({"success": True})
    else:
        return jsonify({"success": False, "error": "Already liked"}), 400

@app.route("/api/likes/<int:activity_id>", methods=["DELETE", "OPTIONS"])
def remove_like(activity_id):
    if request.method == "OPTIONS":
        return '', 204
    _, _, _, likes_manager, _ = managers()
    user_id = session.get("user_id")
    if not user_id:
        return jsonify({"success": False, "error": "Unauthorized"}), 401
    removed = likes_manager.remove_like(user_id, activity_id)
    if removed:
        return jsonify({"success": True})
    else:
        return jsonify({"success": False, "error": "Like not found"}), 404

@app.route("/api/activities/<int:activity_id>/likes", methods=["GET"])
def get_activity_likes(activity_id):
    _, _, _, likes_manager, _ = managers()
    likes = likes_manager.get_likes_for_activity(activity_id)
    result = []
    for l in likes:
        result.append(dict(l))
    return jsonify(result)

@app.route("/api/activities/<int:activity_id>/like_count", methods=["GET"])
def get_like_count(activity_id):
    _, _, _, likes_manager, _ = managers()
    count = likes_manager.count_likes(activity_id)
    return jsonify({"activity_id": activity_id, "like_count": count})

@app.route("/api/users/<int:user_id>/likes", methods=["GET"])
def get_user_likes(user_id):
    _, _, _, likes_manager, _ = managers()
    if session.get("user_id") != user_id:
        return jsonify({"success": False, "error": "Unauthorized"}), 401
    activities = likes_manager.get_liked_activities_by_user(user_id)
    return jsonify([{"activity_id": aid} for aid in activities])

# ---------- REVIEWS / REPLIES ----------

@app.route("/api/activities/<int:activity_id>/replies", methods=["POST", "OPTIONS"])
def add_reply(activity_id):
    if request.method == "OPTIONS":
        return '', 204
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

@app.route("/api/activities/<int:activity_id>/replies", methods=["GET"])
def get_replies_for_activity(activity_id):
    _, _, _, _, review_manager = managers()
    replies = review_manager.get_replies_for_activity(activity_id)
    return jsonify([dict(r) for r in replies])

@app.route("/api/replies/<int:reply_id>", methods=["PUT", "OPTIONS"])
def edit_reply(reply_id):
    if request.method == "OPTIONS":
        return '', 204
    _, _, _, _, review_manager = managers()
    user_id = session.get("user_id")
    content = request.get_json().get("content", "")
    success = review_manager.edit_reply(reply_id, user_id, content)
    return jsonify({"success": success})

@app.route("/api/replies/<int:reply_id>", methods=["DELETE", "OPTIONS"])
def hide_reply(reply_id):
    if request.method == "OPTIONS":
        return '', 204
    _, _, _, _, review_manager = managers()
    user_id = session.get("user_id")
    success = review_manager.hide_reply(reply_id, user_id)
    return jsonify({"success": success})

@app.route("/api/replies/<int:reply_id>/restore", methods=["POST", "OPTIONS"])
def restore_reply(reply_id):
    if request.method == "OPTIONS":
        return '', 204
    _, _, _, _, review_manager = managers()
    user_id = session.get("user_id")
    success = review_manager.restore_reply(reply_id, user_id)
    return jsonify({"success": success})

@app.route("/api/replies/<int:reply_id>", methods=["GET"])
def get_reply(reply_id):
    _, _, _, _, review_manager = managers()
    reply = review_manager.get_reply_by_id(reply_id)
    return jsonify(dict(reply) if reply else None)

# ---------- USER PROFILE ----------

@app.route("/api/users/<int:user_id>", methods=["GET"])
def get_user_profile(user_id):
    _, _, user_manager, _, _ = managers()
    if session.get("user_id") != user_id:
        return jsonify({"success": False, "error": "Unauthorized"}), 401
    user = user_manager.get_user_by_id(user_id)
    return jsonify(dict(user) if user else None)

@app.route("/api/users/<int:user_id>", methods=["PUT", "OPTIONS"])
def update_user_profile(user_id):
    if request.method == "OPTIONS":
        return '', 204
    _, _, user_manager, _, _ = managers()
    if session.get("user_id") != user_id:
        return jsonify({"success": False, "error": "Unauthorized"}), 401
    data = request.get_json()
    updated = user_manager.update_user(
        user_id,
        data.get("username"), data.get("email"), data.get("password")
    )
    return jsonify({"success": updated})

@app.route("/api/users/<int:user_id>", methods=["DELETE", "OPTIONS"])
def soft_delete_user(user_id):
    if request.method == "OPTIONS":
        return '', 204
    _, _, user_manager, _, _ = managers()
    if session.get("user_id") != user_id:
        return jsonify({"success": False, "error": "Unauthorized"}), 401
    deleted = user_manager.soft_delete_user(user_id)
    return jsonify({"success": deleted})

@app.route("/api/users/<int:user_id>/restore", methods=["POST", "OPTIONS"])
def restore_user(user_id):
    if request.method == "OPTIONS":
        return '', 204
    _, _, user_manager, _, _ = managers()
    if session.get("user_id") != user_id:
        return jsonify({"success": False, "error": "Unauthorized"}), 401
    restored = user_manager.restore_user(user_id)
    return jsonify({"success": restored})

if __name__ == "__main__":
    app.run(debug=True)
