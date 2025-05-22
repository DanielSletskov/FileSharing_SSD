import {
  login, logout,
  uploadFile, downloadFile,
  fetchTree, createFolder, renameItem, deleteItem
} from './api.js';

const loginView = document.getElementById('login-view');
const dashView  = document.getElementById('dashboard-view');
const loginForm = document.getElementById('login-form');
const uploadForm = document.getElementById('upload-form');
const fileTreeEl = document.getElementById('file-tree');
const loginErr  = document.getElementById('login-error');
const uploadStatus = document.getElementById('upload-status');
const logoutBtn = document.getElementById('logout-btn');
const newFolderBtn = document.getElementById('new-folder-btn');

function showDashboard() {
  loginView.classList.add('hidden');
  dashView.classList.remove('hidden');
  refreshTree();
}

function showLogin() {
  dashView.classList.add('hidden');
  loginView.classList.remove('hidden');
}

async function refreshTree() {
  fileTreeEl.innerHTML = '<li>Loading…</li>';
  try {
    const tree = await fetchTree();
    renderTree(tree, fileTreeEl);
  } catch (err) {
    fileTreeEl.innerHTML = `<li class="error">${err.message}</li>`;
  }
}

function renderTree(nodes, parentUl) {
  parentUl.innerHTML = '';
  for (const node of nodes) {
    const li = document.createElement('li');
    li.dataset.id = node.id;
    li.classList.add(node.type);

    const nameSpan = document.createElement('span');
    nameSpan.textContent = node.name;
    li.appendChild(nameSpan);

    const actions = document.createElement('span');
    actions.classList.add('item-actions');
    const renameBtn = document.createElement('button');
    renameBtn.textContent = '✏';
    const delBtn = document.createElement('button');
    delBtn.textContent = '🗑';
    actions.append(renameBtn, delBtn);
    li.appendChild(actions);

    if (node.type === 'file') {
      nameSpan.addEventListener('click', () => downloadFile(node.id));
    } else {
      li.classList.add('folder');
      const childUl = document.createElement('ul');
      li.appendChild(childUl);
      nameSpan.addEventListener('click', () => {
        li.classList.toggle('open');
        if (li.classList.contains('open') && childUl.children.length === 0) {
          renderTree(node.children || [], childUl);
        }
      });
    }

    renameBtn.addEventListener('click', async () => {
      const newName = prompt('New name for "' + node.name + '"', node.name);
      if (newName && newName !== node.name) {
        await renameItem(node.id, newName);
        refreshTree();
      }
    });

    delBtn.addEventListener('click', async () => {
      if (confirm(`Delete "${node.name}"?`)) {
        await deleteItem(node.id);
        refreshTree();
      }
    });

    parentUl.appendChild(li);
  }
}

loginForm.addEventListener('submit', async e => {
  e.preventDefault();
  loginErr.textContent = '';
  const user = document.getElementById('username').value;
  const pass = document.getElementById('password').value;
  try {
    await login(user, pass);
    showDashboard();
  } catch (err) {
    loginErr.textContent = err.message;
  }
});

uploadForm.addEventListener('submit', async e => {
  e.preventDefault();
  uploadStatus.textContent = 'Uploading…';
  const file = document.getElementById('file-input').files[0];
  try {
    await uploadFile(file);
    uploadStatus.textContent = 'Upload successful!';
    refreshTree();
  } catch (err) {
    uploadStatus.textContent = 'Error: ' + err.message;
  }
});

newFolderBtn.addEventListener('click', async () => {
  const name = prompt('Folder name');
  if (name) {
    await createFolder(null, name);
    refreshTree();
  }
});

logoutBtn.addEventListener('click', () => {
  logout();
  showLogin();
});

if (localStorage.getItem('jwt')) {
  showDashboard();
} else {
  showLogin();
}
