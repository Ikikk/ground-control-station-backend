# src/api/controllers/page_controller.py
from flask import Blueprint, jsonify, render_template, redirect, url_for

rest_api = Blueprint('rest_api', __name__)

@rest_api.route("/")
def index():
    return redirect(url_for('rest_api.status'))

@rest_api.route("/status")
def status():
    return render_template('status.html', branding=False)

@rest_api.route("/plan")
def plan():
    return redirect("http://localhost:3000/plan")

@rest_api.route("/mission_table")
def mission_table():
    return render_template('mission-table.html', branding=False)