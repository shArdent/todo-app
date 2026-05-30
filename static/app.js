let dragTask = null;

document.querySelectorAll('.task').forEach(el => {
    el.addEventListener('dragstart', onDragStart);
    el.addEventListener('dragend', onDragEnd);
});

document.querySelectorAll('.task-list').forEach(el => {
    el.addEventListener('dragover', onDragOver);
    el.addEventListener('dragenter', onDragEnter);
    el.addEventListener('dragleave', onDragLeave);
    el.addEventListener('drop', onDrop);
});

function onDragStart(e) {
    dragTask = this;
    this.classList.add('dragging');
    e.dataTransfer.effectAllowed = 'move';
    e.dataTransfer.setData('text/plain', this.dataset.id);
}

function onDragEnd() {
    this.classList.remove('dragging');
    dragTask = null;
    document.querySelectorAll('.task-list').forEach(el => el.classList.remove('drag-over'));
}

function onDragOver(e) {
    e.preventDefault();
    e.dataTransfer.dropEffect = 'move';
}

function onDragEnter(e) {
    e.preventDefault();
    this.classList.add('drag-over');
}

function onDragLeave() {
    this.classList.remove('drag-over');
}

function onDrop(e) {
    e.preventDefault();
    this.classList.remove('drag-over');
    if (!dragTask) return;

    const taskId = dragTask.dataset.id;
    const newStatus = this.dataset.status;
    const tasks = [...this.querySelectorAll('.task:not(.dragging)')];

    let insertBefore = null;
    for (const t of tasks) {
        const rect = t.getBoundingClientRect();
        const mid = rect.top + rect.height / 2;
        if (e.clientY < mid) {
            insertBefore = t;
            break;
        }
    }

    let position;
    if (insertBefore) {
        position = parseInt(insertBefore.dataset.position);
        this.insertBefore(dragTask, insertBefore);
    } else {
        position = tasks.length > 0 ? parseInt(tasks[tasks.length - 1].dataset.position) + 1 : 0;
        this.appendChild(dragTask);
    }

    dragTask.dataset.status = newStatus;

    fetch(`/tasks/${taskId}/move`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
        body: `status=${encodeURIComponent(newStatus)}&position=${position}`
    }).then(() => updateCounts());
}

function updateCounts() {
    document.querySelectorAll('.column').forEach(col => {
        const count = col.querySelectorAll('.task').length;
        col.querySelector('.count').textContent = count;
    });
}

function showAddModal() {
    document.getElementById('addModal').classList.add('active');
}

function showEditModal(id) {
    const btn = document.querySelector(`.task[data-id="${id}"] .btn-small`);
    document.getElementById('editTitle').value = btn.dataset.title;
    document.getElementById('editDescription').value = btn.dataset.description;
    const form = document.getElementById('editForm');
    form.action = `/tasks/${id}/edit`;

    form.onsubmit = function(e) {
        e.preventDefault();
        const fd = new FormData(this);
        fetch(this.action, {
            method: 'POST',
            headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
            body: new URLSearchParams(fd)
        }).then(() => {
            closeModals();
            location.reload();
        });
    };
    document.getElementById('editModal').classList.add('active');
}

function closeModals() {
    document.querySelectorAll('.modal-overlay').forEach(el => el.classList.remove('active'));
}
