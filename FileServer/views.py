from flask import Blueprint, request, jsonify, send_file, abort
from flask_login import login_required, current_user
from models import db, Folder, File
from crypto import encrypt_file, decrypt_file, derive_key
from werkzeug.utils import secure_filename
import os, io

main_bp = Blueprint('main', __name__)

def build_tree(parent_id=None):
    tree = []
    folders = Folder.query.filter_by(owner_id=current_user.id,
                                     parent_id=parent_id).all()
    for fld in folders:
        tree.append({
            "type": "folder",
            "id": fld.id,
            "name": fld.name,
            "children": build_tree(fld.id)
        })
    files = File.query.filter_by(owner_id=current_user.id,
                                 folder_id=parent_id).all()
    for f in files:
        tree.append({
            "type": "file",
            "id": f.id,
            "name": f.orig_filename
        })
    return tree

@main_bp.route('/tree', methods=['GET'])
@login_required
def api_tree():
    return jsonify(build_tree(None))

@main_bp.route('/folder', methods=['POST'])
@login_required
def api_create_folder():
    data = request.get_json()
    name = data.get('name')
    parent_id = data.get('parent_id')
    if not name:
        abort(400, "Name required")
    fld = Folder(name=name, owner_id=current_user.id, parent_id=parent_id)
    db.session.add(fld); db.session.commit()
    return jsonify(id=fld.id, name=fld.name), 201

@main_bp.route('/item/<int:item_id>', methods=['PATCH'])
@login_required
def api_rename_item(item_id):
    data = request.get_json(); new_name = data.get('name')
    if not new_name: abort(400, "Name required")
    obj = Folder.query.filter_by(id=item_id, owner_id=current_user.id).first()
    kind = 'folder'
    if not obj:
        obj = File.query.filter_by(id=item_id, owner_id=current_user.id).first()
        kind = 'file'
    if not obj: abort(404)
    if kind == 'folder':
        obj.name = new_name
    else:
        obj.orig_filename = new_name
    db.session.commit()
    return jsonify(id=obj.id, name=new_name)

@main_bp.route('/item/<int:item_id>', methods=['DELETE'])
@login_required
def api_delete_item(item_id):
    fld = Folder.query.filter_by(id=item_id, owner_id=current_user.id).first()
    if fld:
        def delete_folder(f):
            for sub in Folder.query.filter_by(parent_id=f.id,
                                              owner_id=current_user.id):
                delete_folder(sub)
            for file in File.query.filter_by(folder_id=f.id,
                                             owner_id=current_user.id):
                db.session.delete(file)
            db.session.delete(f)
        delete_folder(fld); db.session.commit()
        return '', 204

    f = File.query.filter_by(id=item_id, owner_id=current_user.id).first()
    if f:
        db.session.delete(f); db.session.commit()
        return '', 204

    abort(404)

@main_bp.route('/upload', methods=['POST'])
@login_required
def upload():
    uploaded = request.files['file']
    folder_id = request.form.get('folder_id')
    data = uploaded.read()
    # Derive key from user password (example; adapt as you store it)
    key = derive_key(request.headers.get('X-User-Password'), current_user.key_salt)
    encrypted = encrypt_file(data, key)
    user_dir = os.path.join(os.getenv('STORAGE_DIR'), current_user.username)
    os.makedirs(user_dir, exist_ok=True)
    filename = secure_filename(uploaded.filename) + '.enc'
    path = os.path.join(user_dir, filename)
    with open(path, 'wb') as f: f.write(encrypted)
    meta = File(orig_filename=uploaded.filename,
                stored_path=path,
                owner_id=current_user.id,
                folder_id=folder_id)
    db.session.add(meta); db.session.commit()
    return jsonify(status='ok')

@main_bp.route('/download/<int:file_id>', methods=['GET'])
@login_required
def download(file_id):
    f = File.query.get_or_404(file_id)
    if f.owner_id != current_user.id:
        abort(403)
    encrypted = open(f.stored_path, 'rb').read()
    key = derive_key(request.headers.get('X-User-Password'), current_user.key_salt)
    data = decrypt_file(encrypted, key)
    return send_file(io.BytesIO(data),
                     download_name=f.orig_filename,
                     as_attachment=True)
