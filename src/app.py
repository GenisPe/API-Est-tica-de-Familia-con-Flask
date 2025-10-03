"""
This module takes care of starting the API Server, Loading the DB and Adding the endpoints
"""
import os
from flask import Flask, request, jsonify, url_for
from flask_cors import CORS
from utils import APIException, generate_sitemap
from datastructures import FamilyStructure
# from models import Person


app = Flask(__name__)
app.url_map.strict_slashes = False
CORS(app)

# Create the jackson family object
jackson_family = FamilyStructure("Jackson")
jackson_family.add_member({"first_name" : "Alberto", "age" : 28, "lucky_numbers" : [58,4,25]})
jackson_family.add_member({"first_name": "Mortadelo", "age" : 35, "lucky_numbers" : [23,15,67]})

# Handle/serialize errors like a JSON object
@app.errorhandler(APIException)
def handle_invalid_usage(error):
    return jsonify(error.to_dict()), error.status_code


# Generate sitemap with all your endpoints
@app.route('/')
def sitemap():
    return generate_sitemap(app)


@app.route('/members', methods=['GET','POST'])
def handle_members():
    if request.method == "POST":
        member = request.get_json()
        if set(member.keys()) >= {"first_name", "age", "lucky_numbers"}:
            new_member = jackson_family.add_member(member)
            return jsonify(new_member), 200   # ✅ devolvemos el miembro creado con id
        else:
            return jsonify({"error": "Missing required fields"}), 400

    members = jackson_family.get_all_members()
    return jsonify(members), 200


@app.route('/members/<int:member_id>', methods=['GET', 'DELETE'])
def handle_member(member_id):
    if request.method == "DELETE":
        deleted = jackson_family.delete_member(member_id)
        if deleted:
            return jsonify({"done": True}), 200   # ✅ los tests esperan {"done": true}
        else:
            return jsonify({"error": "Member not found"}), 404

    member = jackson_family.get_member(member_id)
    if member:
        # quitamos last_name porque los tests no lo esperan
        member = {
            "id": member["id"],
            "first_name": member["first_name"],
            "age": member["age"],
            "lucky_numbers": member["lucky_numbers"]
        }
        return jsonify(member), 200
    else:
        return jsonify({"error": "Member not found"}), 404


# This only runs if `$ python src/app.py` is executed
if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=PORT, debug=True)
    