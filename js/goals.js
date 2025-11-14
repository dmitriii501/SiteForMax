// Трекер целей
let goals = [];

document.addEventListener('DOMContentLoaded', async function() {
    await loadGoals();
    setupEventListeners();
    renderGoals();
});

function setupEventListeners() {
    document.getElementById('add-goal-btn').addEventListener('click', toggleGoalForm);
    document.getElementById('save-goal').addEventListener('click', addGoal);
    document.getElementById('cancel-goal').addEventListener('click', toggleGoalForm);
}

async function loadGoals() {
    try {
        goals = await api.goals.getAll();
    } catch (error) {
        console.error('Ошибка загрузки целей:', error);
        goals = [];
    }
}

function toggleGoalForm() {
    const form = document.getElementById('goal-form');
    form.classList.toggle('active');
}

async function addGoal() {
    const title = document.getElementById('goal-title').value.trim();
    const description = document.getElementById('goal-description').value.trim();
    
    if (!title) {
        alert('Пожалуйста, введите название цели');
        return;
    }
    
    try {
        await api.goals.create({
            title,
            description: description || null
        });
        
        // Очистить форму
        document.getElementById('goal-title').value = '';
        document.getElementById('goal-description').value = '';
        
        // Скрыть форму и обновить список
        toggleGoalForm();
        await loadGoals();
        renderGoals();
    } catch (error) {
        console.error('Ошибка создания цели:', error);
        alert('Не удалось создать цель. Проверьте подключение к серверу.');
    }
}

function renderGoals() {
    const container = document.getElementById('goals-list');
    
    if (goals.length === 0) {
        container.innerHTML = '<div class="empty-state">Пока нет целей. Создайте свою первую цель, чтобы начать!</div>';
        return;
    }
    
    container.innerHTML = '';
    
    goals.forEach(goal => {
        const progress = calculateGoalProgress(goal);
        
        const goalElement = document.createElement('div');
        goalElement.className = 'goal-item';
        goalElement.innerHTML = `
            <div class="goal-header">
                <button class="toggle-btn" onclick="toggleGoal('${goal.id}')">
                    <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                        ${goal.expanded ? '<path d="m6 9 6 6 6-6"/>' : '<path d="m9 18 6-6-6-6"/>'}
                    </svg>
                </button>
                <div class="goal-info">
                    <div class="goal-title">${escapeHtml(goal.title)}</div>
                    ${goal.description ? `<div class="goal-description">${escapeHtml(goal.description)}</div>` : ''}
                    <div class="goal-progress">
                        <div class="progress-bar">
                            <div class="progress-fill" style="width: ${progress}%"></div>
                        </div>
                        <div class="progress-text">${Math.round(progress)}%</div>
                    </div>
                </div>
                <button class="delete-btn" onclick="deleteGoal('${goal.id}')">
                    <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                        <polyline points="3 6 5 6 21 6"></polyline>
                        <path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"></path>
                    </svg>
                </button>
            </div>
            ${goal.expanded ? `
                <div class="goal-subtasks">
                    <div class="subtasks-list">
                        ${goal.subtasks.map(subtask => `
                            <div class="subtask-item">
                                <div class="subtask-checkbox ${subtask.completed ? 'checked' : ''}" onclick="toggleSubtask('${goal.id}', '${subtask.id}')"></div>
                                <div class="subtask-title ${subtask.completed ? 'completed' : ''}">${escapeHtml(subtask.title)}</div>
                                <button class="delete-btn" onclick="deleteSubtask('${goal.id}', '${subtask.id}')">
                                    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                                        <polyline points="3 6 5 6 21 6"></polyline>
                                        <path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"></path>
                                    </svg>
                                </button>
                            </div>
                        `).join('')}
                    </div>
                    <input type="text" class="subtask-input" placeholder="Добавить подзадачу..." onkeypress="addSubtaskOnEnter(event, '${goal.id}')">
                </div>
            ` : ''}
        `;
        container.appendChild(goalElement);
    });
}

function calculateGoalProgress(goal) {
    if (!goal.subtasks || goal.subtasks.length === 0) return 0;
    const completed = goal.subtasks.filter(st => st.completed).length;
    return (completed / goal.subtasks.length) * 100;
}

async function toggleGoal(id) {
    try {
        const goal = goals.find(g => g.id === id);
        if (goal) {
            await api.goals.update(id, {
                expanded: !goal.expanded
            });
            await loadGoals();
            renderGoals();
        }
    } catch (error) {
        console.error('Ошибка обновления цели:', error);
        alert('Не удалось обновить цель.');
    }
}

async function toggleSubtask(goalId, subtaskId) {
    try {
        const goal = goals.find(g => g.id === goalId);
        if (goal) {
            const subtask = goal.subtasks.find(st => st.id === subtaskId);
            if (subtask) {
                await api.goals.updateSubtask(goalId, subtaskId, !subtask.completed);
                await loadGoals();
                renderGoals();
            }
        }
    } catch (error) {
        console.error('Ошибка обновления подзадачи:', error);
        alert('Не удалось обновить подзадачу.');
    }
}

function addSubtaskOnEnter(event, goalId) {
    if (event.key === 'Enter') {
        const input = event.target;
        const title = input.value.trim();
        
        if (title) {
            addSubtask(goalId, title);
            input.value = '';
        }
    }
}

async function addSubtask(goalId, title) {
    try {
        await api.goals.createSubtask(goalId, { title });
        await loadGoals();
        renderGoals();
    } catch (error) {
        console.error('Ошибка создания подзадачи:', error);
        alert('Не удалось создать подзадачу.');
    }
}

async function deleteSubtask(goalId, subtaskId) {
    if (confirm('Вы уверены, что хотите удалить эту подзадачу?')) {
        try {
            await api.goals.deleteSubtask(goalId, subtaskId);
            await loadGoals();
            renderGoals();
        } catch (error) {
            console.error('Ошибка удаления подзадачи:', error);
            alert('Не удалось удалить подзадачу.');
        }
    }
}

async function deleteGoal(id) {
    if (confirm('Вы уверены, что хотите удалить эту цель?')) {
        try {
            await api.goals.delete(id);
            await loadGoals();
            renderGoals();
        } catch (error) {
            console.error('Ошибка удаления цели:', error);
            alert('Не удалось удалить цель.');
        }
    }
}

// Вспомогательная функция для экранирования HTML
function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}
