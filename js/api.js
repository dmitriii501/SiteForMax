// API модуль для работы с бэкендом
// Для локальной разработки используйте: 'http://localhost:8000/api'
// Для продакшена измените на относительный путь '/api' или полный URL вашего API

// Автоматическое определение окружения
const isLocalhost = window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1';
const API_BASE_URL = isLocalhost 
    ? 'http://localhost:8000/api'  // Для локальной разработки
    : '/api';  // Относительный путь для продакшена (если API на том же домене)
    // Или укажите полный URL: 'https://api.yourdomain.com/api'

// Общая функция для выполнения запросов
async function apiRequest(endpoint, options = {}) {
    const url = `${API_BASE_URL}${endpoint}`;
    const config = {
        headers: {
            'Content-Type': 'application/json',
            ...options.headers
        },
        ...options
    };

    if (config.body && typeof config.body === 'object') {
        config.body = JSON.stringify(config.body);
    }

    try {
        const response = await fetch(url, config);
        
        if (!response.ok) {
            const error = await response.json().catch(() => ({ detail: response.statusText }));
            throw new Error(error.detail || `HTTP error! status: ${response.status}`);
        }

        // Если ответ пустой (например, при DELETE)
        if (response.status === 204 || response.headers.get('content-length') === '0') {
            return null;
        }

        return await response.json();
    } catch (error) {
        console.error('API request failed:', error);
        throw error;
    }
}

// API для задач (Todos)
const todosAPI = {
    getAll: () => apiRequest('/todos/'),
    getById: (id) => apiRequest(`/todos/${id}`),
    create: (todo) => apiRequest('/todos/', { method: 'POST', body: todo }),
    update: (id, todo) => apiRequest(`/todos/${id}`, { method: 'PUT', body: todo }),
    delete: (id) => apiRequest(`/todos/${id}`, { method: 'DELETE' })
};

// API для целей (Goals)
const goalsAPI = {
    getAll: () => apiRequest('/goals/'),
    getById: (id) => apiRequest(`/goals/${id}`),
    create: (goal) => apiRequest('/goals/', { method: 'POST', body: goal }),
    update: (id, goal) => apiRequest(`/goals/${id}`, { method: 'PUT', body: goal }),
    delete: (id) => apiRequest(`/goals/${id}`, { method: 'DELETE' }),
    createSubtask: (goalId, subtask) => apiRequest(`/goals/${goalId}/subtasks`, { method: 'POST', body: subtask }),
    updateSubtask: (goalId, subtaskId, completed) => apiRequest(`/goals/${goalId}/subtasks/${subtaskId}`, { 
        method: 'PUT', 
        body: { completed } 
    }),
    deleteSubtask: (goalId, subtaskId) => apiRequest(`/goals/${goalId}/subtasks/${subtaskId}`, { method: 'DELETE' })
};

// API для привычек (Habits)
const habitsAPI = {
    getAll: () => apiRequest('/habits/'),
    getById: (id) => apiRequest(`/habits/${id}`),
    create: (habit) => apiRequest('/habits/', { method: 'POST', body: habit }),
    delete: (id) => apiRequest(`/habits/${id}`, { method: 'DELETE' }),
    getCompletions: (habitId, startDate, endDate) => {
        const params = new URLSearchParams();
        if (startDate) params.append('start_date', startDate);
        if (endDate) params.append('end_date', endDate);
        const query = params.toString() ? `?${params.toString()}` : '';
        return apiRequest(`/habits/${habitId}/completions${query}`);
    },
    toggleCompletion: (habitId, date) => apiRequest(`/habits/${habitId}/completions/${date}`, { method: 'POST' }),
    getWaterData: (date) => apiRequest(`/habits/water/${date}`),
    updateWaterData: (date, data) => apiRequest(`/habits/water/${date}`, { method: 'PUT', body: data }),
    addWater: (date, amount = 100) => apiRequest(`/habits/water/${date}/add?amount=${amount}`, { method: 'POST' })
};

// API для настроения (Mood)
const moodAPI = {
    getAll: (startDate, endDate) => {
        const params = new URLSearchParams();
        if (startDate) params.append('start_date', startDate);
        if (endDate) params.append('end_date', endDate);
        const query = params.toString() ? `?${params.toString()}` : '';
        return apiRequest(`/mood/${query}`);
    },
    getByDate: (date) => apiRequest(`/mood/${date}`),
    createOrUpdate: (date, entry) => apiRequest(`/mood/${date}`, { method: 'POST', body: entry }),
    update: (date, entry) => apiRequest(`/mood/${date}`, { method: 'PUT', body: entry }),
    delete: (date) => apiRequest(`/mood/${date}`, { method: 'DELETE' })
};

// API для отчётов (Reports)
const reportsAPI = {
    getStats: () => apiRequest('/reports/stats'),
    getTasksChart: () => apiRequest('/reports/tasks-chart'),
    getMoodChart: () => apiRequest('/reports/mood-chart'),
    getHabitsProgress: () => apiRequest('/reports/habits-progress'),
    getEmotionsChart: () => apiRequest('/reports/emotions-chart'),
    getWeeklyReport: () => apiRequest('/reports/weekly-report')
};

// Вспомогательная функция для форматирования даты
function formatDate(date) {
    if (typeof date === 'string') {
        return date;
    }
    const d = new Date(date);
    return `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}-${String(d.getDate()).padStart(2, '0')}`;
}

// Экспорт API
window.api = {
    todos: todosAPI,
    goals: goalsAPI,
    habits: habitsAPI,
    mood: moodAPI,
    reports: reportsAPI,
    formatDate
};

