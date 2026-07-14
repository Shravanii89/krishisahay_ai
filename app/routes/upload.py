import os
from flask import Blueprint, render_template, request, flash, redirect, url_for, current_app
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
from app.models import db, DocumentUpload
from app.services.ai_service import AIService

upload_bp = Blueprint('upload', __name__)

ALLOWED_EXTENSIONS = {
    'image': {'png', 'jpg', 'jpeg', 'webp'},
    'audio': {'mp3', 'wav', 'ogg', 'm4a'},
    'video': {'mp4', 'avi', 'mov', 'mkv'},
    'text': {'txt', 'pdf', 'doc', 'docx'}
}

def get_file_category(filename):
    ext = filename.rsplit('.', 1)[-1].lower() if '.' in filename else ''
    for category, extensions in ALLOWED_EXTENSIONS.items():
        if ext in extensions:
            return category
    return None

@upload_bp.route('/', methods=['GET', 'POST'])
@login_required
def upload_center():
    if request.method == 'POST':
        if 'document' not in request.files:
            flash('No file selected.', 'danger')
            return redirect(request.url)
            
        file = request.files['document']
        
        if file.filename == '':
            flash('No file selected.', 'danger')
            return redirect(request.url)
            
        category = get_file_category(file.filename)
        if not category:
            flash('Unsupported file type. Please upload images, audio, video, or documents (PDF/Text).', 'danger')
            return redirect(request.url)
            
        # Secure and save
        filename = secure_filename(file.filename)
        # Prefix with user ID to prevent name collisions
        saved_filename = f"user_{current_user.id}_{filename}"
        file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], saved_filename)
        
        try:
            file.save(file_path)
            
            # Create Database Record
            new_upload = DocumentUpload(
                user_id=current_user.id,
                file_path=os.path.join('static', 'uploads', saved_filename),
                file_type=category,
                ai_status="Pending"
            )
            db.session.add(new_upload)
            db.session.commit()
            
            # Simulate immediate AI evaluation
            ai_service = AIService()
            analysis = ai_service.analyze_document(file_path, category)
            
            # Update database record
            new_upload.ai_status = "Completed"
            # Serialize analysis summary to database
            new_upload.ai_result = str(analysis)
            db.session.commit()
            
            flash(f"File uploaded successfully! KrishiSahay AI has scanned it: {analysis.get('summary', 'Analysis completed.')}", 'success')
            return redirect(url_for('upload.upload_center'))
            
        except Exception as e:
            db.session.rollback()
            flash(f"Error handling upload: {str(e)}", 'danger')
            return redirect(request.url)
            
    # GET request - show history of uploads
    uploads = DocumentUpload.query.filter_by(user_id=current_user.id).order_by(DocumentUpload.uploaded_at.desc()).all()
    
    # Parse mock details from string representation for display in UI
    parsed_uploads = []
    import ast
    for u in uploads:
        result_dict = {}
        if u.ai_result:
            try:
                # Convert string dict back safely
                result_dict = ast.literal_eval(u.ai_result)
            except Exception:
                result_dict = {"summary": u.ai_result}
        parsed_uploads.append({
            'record': u,
            'details': result_dict
        })
        
    return render_template('upload.html', uploads=parsed_uploads)
