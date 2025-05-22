// … existing imports and API_BASE …

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
  return apiRequest(`/item/${id}`, {
    method: 'DELETE'
  });
}
