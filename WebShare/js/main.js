import {
  login, listFiles, uploadFile, downloadFile, logout,
  fetchTree, createFolder, renameItem, deleteItem
} from './api.js';

const fileTreeEl = document.getElementById('file-tree');
const newFolderBtn = document.getElementById('new-folder-btn');

// Render the tree recursively
function renderTree(nodes, parentUl) {
  parentUl.innerHTML = '';
  for (const node of nodes) {
    const li = document.createElement('li');
    li.dataset.id = node.id;
    li.classList.add(node.type);

    const nameSpan = document.createElement('span');
    nameSpan.textContent = node.name;
    li.appendChild(nameSpan);

    // Actions: rename & delete
    const actions = document.createElement('span');
    actions.classList.add('item-actions');
    const renameBtn = document.createElement('button');
    renameBtn.textContent = '✏';
    const delBtn = document.createElement('button');
    delBtn.textContent = '🗑';
    actions.append(renameBtn, delBtn);
    li.appendChild(actions);

    // File click = download
    if (node.type === 'file') {
      nameSpan.addEventListener('click', () => downloadFile(node.id));
    } else {
      // Folder expand/collapse
      li.classList.add('folder');
      const childUl = document.createElement('ul');
      li.appendChild(childUl);
      nameSpan.addEventListener('click', () => {
        li.classList.toggle('open');
        if (li.classList.contains('open') && childUl.children.length===0) {
          // load children on first expand
          renderTree(node.children || [], childUl);
        }
      });
    }

    // Rename handler
    renameBtn.addEventListener('click', async () => {
      const newName = prompt('New name for "' + node.name + '"', node.name);
      if (newName && newName !== node.name) {
        await renameItem(node.id, newName);
        refreshTree();
      }
    });

    // Delete handler
    delBtn.addEventListener('click', async () => {
      if (confirm(`Delete "${node.name}"?`)) {
        await deleteItem(node.id);
        refreshTree();
      }
    });

    parentUl.appendChild(li);
  }
}

// Fetch & render the entire tree
async function refreshTree() {
  fileTreeEl.innerHTML = '<li>Loading…</li>';
  try {
    const tree = await fetchTree();
    renderTree(tree, fileTreeEl);
  } catch (err) {
    fileTreeEl.innerHTML = `<li class="error">${err.message}</li>`;
  }
}

// New‐folder flow (creates at root)
newFolderBtn.addEventListener('click', async () => {
  const name = prompt('Folder name');
  if (name) {
    await createFolder(null, name);
    refreshTree();
  }
});

// Hook into login/upload/logout as before, but replace refreshFiles() calls with refreshTree()
loginForm.addEventListener('submit', /*…*/ async () => {
  /* after successful login… */ showDashboard();
});

uploadForm.addEventListener('submit', /*…*/ async () => {
  await uploadFile(file);
  uploadStatus.textContent = 'Upload successful!';
  refreshTree();
});

logoutBtn.addEventListener('click', () => {
  logout();
  showLogin();
});

// On load…
if (localStorage.getItem('jwt')) {
  showDashboard();
  refreshTree();
} else {
  showLogin();
}
