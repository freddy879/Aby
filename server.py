from flask import Flask, request, jsonify
from flask_cors import CORS
from pymongo import MongoClient
from bson import ObjectId
import os
from datetime import datetime

app = Flask(__name__)

# ==========================================
# CORS
# ==========================================

CORS(app)

# ==========================================
# MONGODB
# ==========================================

MONGO_URI = os.getenv("MONGO_URI")

client = MongoClient(MONGO_URI)

db = client["nexus"]

posts_collection = db["posts"]

# ==========================================
# HOME
# ==========================================

@app.route("/")
def home():

    return jsonify({
        "status":"online",
        "service":"NEXUS SERVER"
    })

# ==========================================
# CREATE POST
# ==========================================

@app.route("/posts", methods=["POST"])
def create_post():

    try:

        data = request.json

        new_post = {

            "author": data.get("author"),
            "initials": data.get("initials"),
            "role": data.get("role"),
            "color": data.get("color"),

            "text": data.get("text"),

            "media": data.get("media", []),

            "likes": 0,

            "created_at": datetime.utcnow().isoformat()

        }

        result = posts_collection.insert_one(new_post)

        new_post["_id"] = str(result.inserted_id)

        return jsonify(new_post)

    except Exception as e:

        return jsonify({
            "success":False,
            "error":str(e)
        }),500

# ==========================================
# GET POSTS
# ==========================================

@app.route("/posts", methods=["GET"])
def get_posts():

    try:

        posts = []

        for post in posts_collection.find().sort("_id",-1):

            post["_id"] = str(post["_id"])

            posts.append(post)

        return jsonify(posts)

    except Exception as e:

        return jsonify({
            "success":False,
            "error":str(e)
        }),500

# ==========================================
# LIKE POST
# ==========================================

@app.route("/like/<post_id>", methods=["POST"])
def like_post(post_id):

    try:

        post = posts_collection.find_one({
            "_id": ObjectId(post_id)
        })

        if not post:

            return jsonify({
                "success":False
            }),404

        likes = post.get("likes",0) + 1

        posts_collection.update_one(
            {"_id":ObjectId(post_id)},
            {"$set":{"likes":likes}}
        )

        return jsonify({
            "success":True,
            "likes":likes
        })

    except Exception as e:

        return jsonify({
            "success":False,
            "error":str(e)
        }),500

# ==========================================
# DELETE POST
# ==========================================

@app.route("/posts/<post_id>", methods=["DELETE"])
def delete_post(post_id):

    try:

        posts_collection.delete_one({
            "_id":ObjectId(post_id)
        })

        return jsonify({
            "success":True
        })

    except Exception as e:

        return jsonify({
            "success":False,
            "error":str(e)
        }),500

# ==========================================
# START
# ==========================================

if __name__ == "__main__":

    port = int(os.environ.get("PORT",5000))

    app.run(
        host="0.0.0.0",
        port=port
    )
