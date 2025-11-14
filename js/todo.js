// Список дел
let todos = [];

document.addEventListener('DOMContentLoaded', async function() {
    console.log('Список дел загружен');
    await loadTodos();
    setupEventListeners();
    renderTodos();
});

function setupEventListeners() {
    document.getElementById('add-todo-btn').addEventListener('click', toggleTodoForm);
    document.getElementById('save-todo').addEventListener('click', addTodo);
    document.getElementById('cancel-todo').addEventListener('click', toggleTodoForm);
}

async function loadTodos() {
    try {
        todos = await api.todos.getAll();
        console.log('Загружены задачи:', todos);
    } catch (error) {
        console.error('Ошибка загрузки задач:', error);
        todos = [];
    }
}

function toggleTodoForm() {
    const form = document.getElementById('todo-form');
    form.classList.toggle('active');
}

async function addTodo() {
    const titleInput = document.getElementById('todo-title');
    const descriptionInput = document.getElementById('todo-description');
    const dateInput = document.getElementById('todo-date');
    const timeInput = document.getElementById('todo-time');
    
    const title = titleInput.value.trim();
    const description = descriptionInput.value.trim();
    const dueDate = dateInput.value;
    const reminder = timeInput.value;
    
    if (!title) {
        alert('Пожалуйста, введите название задачи');
        return;
    }
    
    try {
        const newTodo = await api.todos.create({
            title,
            description: description || null,
            due_date: dueDate || null,
            reminder: reminder || null
        });
        
        // Очистить форму
        titleInput.value = '';
        descriptionInput.value = '';
        dateInput.value = '';
        timeInput.value = '';
        
        // Скрыть форму и обновить список
        toggleTodoForm();
        await loadTodos();
        renderTodos();
    } catch (error) {
        console.error('Ошибка создания задачи:', error);
        alert('Не удалось создать задачу. Проверьте подключение к серверу.');
    }
}

function renderTodos() {
    const container = document.getElementById('tasks-list');
    console.log('Отрисовка задач:', todos);
    
    if (!todos || todos.length === 0) {
        container.innerHTML = '<div class="empty-state">Пока нет задач. Создайте свою первую задачу, чтобы начать!</div>';
        return;
    }
    
    // Сортируем задачи: сначала невыполненные, потом выполненные
    const sortedTodos = [...todos].sort((a, b) => {
        if (a.completed && !b.completed) return 1;
        if (!a.completed && b.completed) return -1;
        return 0;
    });
    
    container.innerHTML = '';
    
    sortedTodos.forEach(todo => {
        const todoElement = document.createElement('div');
        todoElement.className = 'task-item';
        if (todo.completed) {
            todoElement.classList.add('completed-task');
        }
        todoElement.innerHTML = `
            <div class="task-checkbox ${todo.completed ? 'checked' : ''}" onclick="toggleTodo('${todo.id}')"></div>
            <div class="task-content">
                <div class="task-title ${todo.completed ? 'completed' : ''}">${escapeHtml(todo.title)}</div>
                ${todo.description ? `<div class="task-description">${escapeHtml(todo.description)}</div>` : ''}
                <div class="task-meta">
                    ${todo.due_date ? `<div class="task-meta-item">
                        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                            <rect x="3" y="4" width="18" height="18" rx="2" ry="2"></rect>
                            <line x1="16" y1="2" x2="16" y2="6"></line>
                            <line x1="8" y1="2" x2="8" y2="6"></line>
                            <line x1="3" y1="10" x2="21" y2="10"></line>
                        </svg>
                        ${formatDate(todo.due_date)}
                    </div>` : ''}
                    ${todo.reminder ? `<div class="task-meta-item">
                        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                            <circle cx="12" cy="12" r="10"></circle>
                            <polyline points="12 6 12 12 16 14"></polyline>
                        </svg>
                        ${escapeHtml(todo.reminder)}
                    </div>` : ''}
                </div>
            </div>
            <div class="task-actions">
                <button class="edit-btn" onclick="editTodo('${todo.id}')">
                    <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                        <path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"></path>
                        <path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z"></path>
                    </svg>
                </button>
                <button class="delete-btn" onclick="deleteTodo('${todo.id}')">
                    <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                        <polyline points="3 6 5 6 21 6"></polyline>
                        <path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"></path>
                    </svg>
                </button>
            </div>
        `;
        container.appendChild(todoElement);
    });
}

async function toggleTodo(id) {
    try {
        const todo = todos.find(t => t.id === id);
        if (todo) {
            await api.todos.update(id, {
                completed: !todo.completed
            });
            
            // Обновляем локальный список
            await loadTodos();
            
            // Сразу обновляем галочку
            const taskElement = document.querySelector(`[onclick="toggleTodo('${id}')"]`)?.closest('.task-item');
            if (taskElement) {
                const checkbox = taskElement.querySelector('.task-checkbox');
                const updatedTodo = todos.find(t => t.id === id);
                if (updatedTodo?.completed) {
                    checkbox.classList.add('checked');
                    taskElement.querySelector('.task-title').classList.add('completed');
                    taskElement.classList.add('completed-task');
                    setTimeout(() => {
                        renderTodos();
                    }, 1000);
                } else {
                    checkbox.classList.remove('checked');
                    taskElement.querySelector('.task-title').classList.remove('completed');
                    taskElement.classList.remove('completed-task');
                    renderTodos();
                }
            } else {
                renderTodos();
            }
        }
    } catch (error) {
        console.error('Ошибка обновления задачи:', error);
        alert('Не удалось обновить задачу.');
    }
}

async function deleteTodo(id) {
    try {
        await api.todos.delete(id);
        await loadTodos();
        renderTodos();
    } catch (error) {
        console.error('Ошибка удаления задачи:', error);
        alert('Не удалось удалить задачу.');
    }
}

function formatDate(dateString) {
    try {
        const date = new Date(dateString);
        return date.toLocaleDateString('ru-RU');
    } catch (e) {
        return dateString;
    }
}

// Функция для открытия модального окна редактирования
function editTodo(id) {
    const todo = todos.find(t => t.id === id);
    if (todo) {
        // Заполняем форму данными задачи
        document.getElementById('edit-todo-id').value = todo.id;
        document.getElementById('edit-todo-title').value = todo.title;
        document.getElementById('edit-todo-description').value = todo.description || '';
        document.getElementById('edit-todo-date').value = todo.due_date || '';
        document.getElementById('edit-todo-time').value = todo.reminder || '';
        
        // Показываем модальное окно
        document.getElementById('edit-todo-modal').style.display = 'flex';
    }
}

// Функция для сохранения изменений
async function saveEditedTodo() {
    const id = document.getElementById('edit-todo-id').value;
    const title = document.getElementById('edit-todo-title').value.trim();
    const description = document.getElementById('edit-todo-description').value.trim();
    const dueDate = document.getElementById('edit-todo-date').value;
    const reminder = document.getElementById('edit-todo-time').value;
    
    if (!title) {
        alert('Пожалуйста, введите название задачи');
        return;
    }
    
    try {
        await api.todos.update(id, {
            title,
            description: description || null,
            due_date: dueDate || null,
            reminder: reminder || null
        });
        
        await loadTodos();
        renderTodos();
        closeEditModal();
    } catch (error) {
        console.error('Ошибка обновления задачи:', error);
        alert('Не удалось обновить задачу.');
    }
}

// Функция для закрытия модального окна
function closeEditModal() {
    document.getElementById('edit-todo-modal').style.display = 'none';
    // Очищаем форму
    document.getElementById('edit-todo-id').value = '';
    document.getElementById('edit-todo-title').value = '';
    document.getElementById('edit-todo-description').value = '';
    document.getElementById('edit-todo-date').value = '';
    document.getElementById('edit-todo-time').value = '';
}

// Вспомогательная функция для экранирования HTML
function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}
