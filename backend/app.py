from flask import Flask, request, jsonify, session
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from werkzeug.utils import secure_filename
import os
import uuid
from datetime import datetime
from llm_integration import LLMIntegration
from code_executor import CodeExecutor

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-here'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///survey_platform.db'
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

db = SQLAlchemy(app)
CORS(app)

# Initialize LLM integration
llm = LLMIntegration()

# Ensure upload directory exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Database Models
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    workspaces = db.relationship('Workspace', backref='owner', lazy=True)

class Workspace(db.Model):
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = db.Column(db.String(100), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    documents = db.relationship('Document', backref='workspace', lazy=True)
    queries = db.relationship('Query', backref='workspace', lazy=True)

class Document(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(255), nullable=False)
    file_path = db.Column(db.String(500), nullable=False)
    doc_type = db.Column(db.String(50))  # 'survey_design' or 'data'
    workspace_id = db.Column(db.String(36), db.ForeignKey('workspace.id'), nullable=False)
    uploaded_at = db.Column(db.DateTime, default=datetime.utcnow)

class Query(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    workspace_id = db.Column(db.String(36), db.ForeignKey('workspace.id'), nullable=False)
    user_query = db.Column(db.Text, nullable=False)
    llm_plan = db.Column(db.Text)
    generated_code = db.Column(db.Text)
    status = db.Column(db.String(20), default='pending')  # pending, approved, rejected, executed
    result = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

# Routes
@app.route('/api/workspaces', methods=['GET', 'POST'])
def workspaces():
    if request.method == 'POST':
        data = request.json
        workspace = Workspace(
            name=data['name'],
            user_id=1  # TODO: Get from session/auth
        )
        db.session.add(workspace)
        db.session.commit()
        return jsonify({'id': workspace.id, 'name': workspace.name})
    
    workspaces = Workspace.query.filter_by(user_id=1).all()  # TODO: Get from session/auth
    return jsonify([{'id': w.id, 'name': w.name, 'created_at': w.created_at} for w in workspaces])

@app.route('/api/workspaces/<workspace_id>/upload', methods=['POST'])
def upload_document(workspace_id):
    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400
    
    file = request.files['file']
    doc_type = request.form.get('doc_type', 'data')
    
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    
    filename = secure_filename(file.filename)
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], workspace_id, filename)
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    file.save(file_path)
    
    document = Document(
        filename=filename,
        file_path=file_path,
        doc_type=doc_type,
        workspace_id=workspace_id
    )
    db.session.add(document)
    db.session.commit()
    
    return jsonify({'id': document.id, 'filename': document.filename})

@app.route('/api/workspaces/<workspace_id>/documents', methods=['GET'])
def get_documents(workspace_id):
    documents = Document.query.filter_by(workspace_id=workspace_id).all()
    return jsonify([{
        'id': d.id,
        'filename': d.filename,
        'doc_type': d.doc_type,
        'uploaded_at': d.uploaded_at
    } for d in documents])

@app.route('/api/workspaces/<workspace_id>/query', methods=['POST'])
def submit_query(workspace_id):
    data = request.json
    user_query = data.get('query')
    
    # Get documents info for this workspace
    documents = Document.query.filter_by(workspace_id=workspace_id).all()
    documents_info = [{
        'filename': d.filename,
        'path': d.file_path,
        'type': d.doc_type
    } for d in documents]
    
    # Generate plan and code using LLM
    plan, code = llm.generate_plan_and_code(user_query, documents_info)
    
    query = Query(
        workspace_id=workspace_id,
        user_query=user_query,
        llm_plan=plan,
        generated_code=code,
        status='pending'
    )
    db.session.add(query)
    db.session.commit()
    
    return jsonify({
        'id': query.id,
        'plan': query.llm_plan,
        'code': query.generated_code,
        'status': query.status
    })

@app.route('/api/queries/<query_id>/approve', methods=['POST'])
def approve_query(query_id):
    query = Query.query.get_or_404(query_id)
    action = request.json.get('action')  # 'approve' or 'reject'
    
    if action == 'approve':
        query.status = 'approved'
        
        # Get workspace and documents
        workspace = Workspace.query.get(query.workspace_id)
        documents = Document.query.filter_by(workspace_id=query.workspace_id).all()
        data_files = [{
            'filename': d.filename,
            'path': d.file_path
        } for d in documents if d.doc_type == 'data']
        
        # Execute the code
        workspace_dir = os.path.join(app.config['UPLOAD_FOLDER'], query.workspace_id)
        executor = CodeExecutor(workspace_dir)
        
        # Validate code first
        is_valid, validation_msg = executor.validate_code(query.generated_code)
        if not is_valid:
            query.status = 'failed'
            query.result = f"Code validation failed: {validation_msg}"
        else:
            # Execute the code
            execution_results = executor.execute_code(query.generated_code, data_files)
            
            if execution_results['success']:
                query.status = 'executed'
                query.result = f"""Execution successful!
                
Output:
{execution_results['output']}

Files created: {', '.join(execution_results['files_created'])}
Execution time: {execution_results['execution_time']:.2f} seconds"""
            else:
                query.status = 'failed'
                query.result = f"Execution failed: {execution_results['error']}"
    else:
        query.status = 'rejected'
    
    db.session.commit()
    return jsonify({'status': query.status, 'result': query.result})

@app.route('/api/queries/<query_id>/refine', methods=['POST'])
def refine_plan(query_id):
    query = Query.query.get_or_404(query_id)
    feedback = request.json.get('feedback')
    
    # Get refined plan and code from LLM
    refined_plan, refined_code = llm.refine_plan(
        query.user_query,
        query.llm_plan,
        query.generated_code,
        feedback
    )
    
    query.llm_plan = refined_plan
    query.generated_code = refined_code
    query.status = 'pending'
    
    db.session.commit()
    return jsonify({
        'plan': query.llm_plan,
        'code': query.generated_code
    })

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True) 