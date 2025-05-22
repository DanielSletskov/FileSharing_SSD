// Base URL of your Ubuntu server API
const API_BASE = 'https://your.server.domain/api';

async function apiRequest(path, opts = {}) {
  const token = localStorage.getItem('jwt');
  const headers = opts.headers || {};
  if (token) headers['Authorization'] = 'Bearer ' + token;
  const res = await fetch(API_BASE + path, {
    credentials: 'include',
    ...opts,
    headers
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.message || res.statusText);
  }
  return res.json();
}

export async function login(username, password) {
  const data = await apiRequest('/login', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ username, password })
  });
  localStorage.setItem('jwt', data.token);
}

export async function logout() {
  localStorage.removeItem('jwt');
}

export async function uploadFile(file, folderId = null) {
  const fd = new FormData();
  if (folderId) fd.append('folder_id', folderId);
  fd.append('file', file);
  return apiRequest('/upload', {
    method: 'POST',
    body: fd
  });
}

export async function downloadFile(fileId) {
  const token = localStorage.getItem('jwt');
  const res = await fetch(API_BASE + `/download/${fileId}`, {
    method: 'GET',
    headers: { 'Authorization': 'Bearer ' + token }
  });
  if (!res.ok) throw new Error('Download failed');
  const blob = await res.blob();
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = '';
  document.body.appendChild(a);
  a.click();
  a.remove();
  URL.revokeObjectURL(url);
}

export async function fetchTree() {
  return apiRequest('/tree');
}

export async function createFolder(parentId, name) {
  return apiRequest('/folder', {
    method: 'POST',
    headers: {'Content-Type':'application/json'},
    body: JSON.stringify({ parent_id: parentId, name })
  });
}

export async function renameItem(id, newName) {
  return apiRequest(`/item/${id}`, {
    method: 'PATCH',
    headers: {'Content-Type':'application/json'},
    body: JSON.stringify({ name: newName })
  });
}

export async function deleteItem(id) {
  return apiRequest(`/item/${id}`, { method: 'DELETE' });
}

