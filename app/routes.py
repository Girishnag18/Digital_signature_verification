from flask import Blueprint, render_template, redirect, url_for, request, flash, current_app, Response, jsonify
from flask_login import login_user, logout_user, login_required, current_user
from app.models import User, DocumentLog
from app.forms import LoginForm, RegistrationForm
from app.head import db

bp = Blueprint('main', __name__)

@bp.route('/')
def index():
    return redirect(url_for('main.login'))

@bp.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = db.session.execute(
            db.select(User).filter_by(username=form.username.data)
        ).scalar_one_or_none()
        if user and user.verify_password(form.password.data):
            login_user(user)
            return redirect(url_for('main.dashboard'))
        flash('Invalid credentials')
    return render_template('login.html', form=form)

@bp.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html')

import os
import json
from werkzeug.utils import secure_filename
from app.utils.signature_verifier import verify_pdf_signature, verify_pdf_signature_stream

@bp.route('/upload', methods=['GET', 'POST'])
@login_required
def upload():
    if request.method == 'POST':
        file = request.files.get('document')
        if file and file.filename and file.filename.endswith('.pdf'):
            filename = secure_filename(file.filename)
            
            # Create uploads directory if it doesn't exist
            upload_dir = os.path.join(current_app.root_path, 'uploads')
            os.makedirs(upload_dir, exist_ok=True)
            
            save_path = os.path.join(upload_dir, filename)
            file.save(save_path)

            # Call signature verification function (non-streaming fallback)
            try:
                result, message = verify_pdf_signature(save_path)
            except Exception as e:
                result, message = False, f"Verification error: {str(e)}"

            # Log to database
            log_entry = DocumentLog(
                document_name=filename,
                user_id=current_user.id,
                action=f"Upload and verify: {message}",
                ip_address=request.remote_addr
            )
            db.session.add(log_entry)
            db.session.commit()

            flash(message, 'success' if result else 'danger')
            return redirect(url_for('main.dashboard'))
        else:
            flash('Please select a valid PDF file.', 'danger')

    return render_template('upload.html')


@bp.route('/upload_ajax', methods=['POST'])
@login_required
def upload_ajax():
    """AJAX upload that saves the PDF and returns its server path for streaming verification."""
    file = request.files.get('document')
    if not file or not file.filename or not file.filename.lower().endswith('.pdf'):
        return jsonify({"error": "Please select a valid PDF file."}), 400

    from werkzeug.utils import secure_filename
    filename = secure_filename(file.filename)

    upload_dir = os.path.join(current_app.root_path, 'uploads')
    os.makedirs(upload_dir, exist_ok=True)

    save_path = os.path.join(upload_dir, filename)
    try:
        file.save(save_path)
    except Exception as e:
        return jsonify({"error": f"Failed to save file: {e}"}), 500

    return jsonify({"saved_path": save_path, "filename": filename})


@bp.route('/verify/stream', methods=['POST'])
@login_required
def verify_stream():
    """SSE endpoint: send real-time verification progress for an uploaded PDF path."""
    data = request.get_json(silent=True) or {}
    pdf_path = data.get('pdf_path')
    trust_roots = data.get('trust_roots')  # optional list of PEM paths
    if not pdf_path or not os.path.exists(pdf_path):
        return jsonify({"error": "pdf_path is required and must exist."}), 400

    def event_stream():
        for evt in verify_pdf_signature_stream(pdf_path, trust_roots_pem=trust_roots):
            yield f"data: {json.dumps(evt)}\n\n"

    headers = {
        'Content-Type': 'text/event-stream',
        'Cache-Control': 'no-cache',
        'X-Accel-Buffering': 'no'  # hint for proxies not to buffer
    }
    return Response(event_stream(), headers=headers)


@bp.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        existing_user = db.session.execute(
            db.select(User).filter_by(username=form.username.data)
        ).scalar_one_or_none()
        if existing_user:
            flash('Username already exists. Please choose a different one.')
            return redirect(url_for('main.register'))

        new_user = User(username=form.username.data)
        new_user.set_password(form.password.data)
        db.session.add(new_user)
        db.session.commit()
        flash('Registration successful. Please log in.')
        return redirect(url_for('main.login'))
    return render_template('register.html', form=form)

@bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.')
    return redirect(url_for('main.login'))
