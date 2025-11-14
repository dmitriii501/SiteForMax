// Трекер привычек
let habits = [];
let waterAmount = 0;
let waterGoal = 2000;
let currentWeekOffset = 0;
let habitCompletions = {}; // {habitId: {date: completed}}

document.addEventListener('DOMContentLoaded', async function() {
    await loadHabits();
    await loadWaterData();
    setupEventListeners();
    await renderHabits();
    renderWaterTracker();
});

function setupEventListeners() {
    document.getElementById('add-habit-btn').addEventListener('click', showHabitModal);
    document.getElementById('close-habit-modal').addEventListener('click', hideHabitModal);
    document.getElementById('save-habit').addEventListener('click', addHabit);
    document.getElementById('add-water').addEventListener('click', addWater);
    document.getElementById('update-water-goal').addEventListener('click', updateWaterGoal);
    document.getElementById('clear-water').addEventListener('click', clearWater);
    
    // Обработчик для кнопки календаря
    document.addEventListener('click', function(e) {
        if (e.target.closest('#water-calendar-btn')) {
            toggleWaterCalendar();
        }
    });
}

async function loadHabits() {
    try {
        habits = await api.habits.getAll();
        // Загружаем отметки выполнения для всех привычек
        await loadHabitCompletions();
    } catch (error) {
        console.error('Ошибка загрузки привычек:', error);
        habits = [];
    }
}

async function loadHabitCompletions() {
    habitCompletions = {};
    const weekDays = getWeekDays(currentWeekOffset);
    const startDate = weekDays[0].fullDate;
    const endDate = weekDays[6].fullDate;
    
    for (const habit of habits) {
        try {
            const completions = await api.habits.getCompletions(habit.id, startDate, endDate);
            habitCompletions[habit.id] = {};
            completions.forEach(comp => {
                if (comp.completed) {
                    habitCompletions[habit.id][comp.date] = true;
                }
            });
        } catch (error) {
            console.error(`Ошибка загрузки отметок для привычки ${habit.id}:`, error);
            habitCompletions[habit.id] = {};
        }
    }
}

async function loadWaterData() {
    const today = new Date();
    const todayFormatted = api.formatDate(today);
    
    try {
        const data = await api.habits.getWaterData(todayFormatted);
        waterAmount = data.amount || 0;
        waterGoal = data.goal || 2000;
    } catch (error) {
        console.error('Ошибка загрузки данных о воде:', error);
        waterAmount = 0;
        waterGoal = 2000;
    }
}

function showHabitModal() {
    document.getElementById('habit-modal').style.display = 'flex';
}

function hideHabitModal() {
    document.getElementById('habit-modal').style.display = 'none';
    document.getElementById('habit-name').value = '';
}

async function addHabit() {
    const name = document.getElementById('habit-name').value.trim();
    
    if (!name) {
        alert('Пожалуйста, введите название привычки');
        return;
    }
    
    try {
        await api.habits.create({ name });
        hideHabitModal();
        await loadHabits();
        await renderHabits();
    } catch (error) {
        console.error('Ошибка создания привычки:', error);
        alert('Не удалось создать привычку. Проверьте подключение к серверу.');
    }
}

// Функция для получения дней недели с датами
function getWeekDays(weekOffset = 0) {
    const days = [];
    const now = new Date();
    
    const monday = new Date(now);
    monday.setDate(now.getDate() - now.getDay() + 1 + (weekOffset * 7));
    
    for (let i = 0; i < 7; i++) {
        const day = new Date(monday);
        day.setDate(monday.getDate() + i);
        
        days.push({
            date: day,
            dayName: getShortDayName(day.getDay()),
            dateNumber: day.getDate(),
            month: day.getMonth() + 1,
            fullDate: api.formatDate(day)
        });
    }
    
    return days;
}

function getShortDayName(dayIndex) {
    const days = ['Вс', 'Пн', 'Вт', 'Ср', 'Чт', 'Пт', 'Сб'];
    return days[dayIndex];
}

function formatDisplayDate(date) {
    const today = new Date();
    const yesterday = new Date(today);
    yesterday.setDate(yesterday.getDate() - 1);
    
    const dateStr = api.formatDate(date);
    const todayStr = api.formatDate(today);
    const yesterdayStr = api.formatDate(yesterday);
    
    if (dateStr === todayStr) {
        return 'Сегодня';
    } else if (dateStr === yesterdayStr) {
        return 'Вчера';
    } else {
        return `${date.getDate().toString().padStart(2, '0')}.${(date.getMonth() + 1).toString().padStart(2, '0')}`;
    }
}

function isToday(date) {
    const today = new Date();
    return date.getDate() === today.getDate() && 
           date.getMonth() === today.getMonth() && 
           date.getFullYear() === today.getFullYear();
}

async function renderHabits() {
    const container = document.getElementById('habits-list');
    
    if (habits.length === 0) {
        container.innerHTML = '<div class="empty-state">Пока нет привычек. Создайте свою первую привычку, чтобы начать!</div>';
        return;
    }
    
    // Загружаем отметки для текущей недели
    await loadHabitCompletions();
    
    container.innerHTML = '';
    
    const weekDays = getWeekDays(currentWeekOffset);
    
    habits.forEach(habit => {
        const habitElement = document.createElement('div');
        habitElement.className = 'habit-item';
        
        const weekNav = `
            <div class="week-navigation">
                <button class="nav-arrow prev-week" onclick="changeWeek(-1)">
                    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                        <polyline points="15 18 9 12 15 6"></polyline>
                    </svg>
                </button>
                <div class="week-dates">
                    ${formatWeekRange(weekDays)}
                </div>
                <button class="nav-arrow next-week" onclick="changeWeek(1)" ${currentWeekOffset >= 0 ? 'disabled style="opacity:0.3"' : ''}>
                    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                        <polyline points="9 18 15 12 9 6"></polyline>
                    </svg>
                </button>
            </div>
        `;
        
        const daysTracker = `
            <div class="habit-days">
                ${weekDays.map(day => {
                    const isCompleted = habitCompletions[habit.id]?.[day.fullDate] || false;
                    const isTodayDate = isToday(day.date);
                    return `
                        <div class="day-container">
                            <button class="day-circle-btn ${isCompleted ? 'completed' : ''} ${isTodayDate ? 'today' : ''}" 
                                    onclick="toggleHabitDay('${habit.id}', '${day.fullDate}')"
                                    data-date="${day.fullDate}">
                                ${isCompleted ? `
                                    <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                                        <polyline points="20 6 9 17 4 12"></polyline>
                                    </svg>
                                ` : day.dateNumber}
                            </button>
                        </div>
                    `;
                }).join('')}
            </div>
        `;
        
        habitElement.innerHTML = `
            <div class="habit-header">
                <h3 class="habit-name">${escapeHtml(habit.name)}</h3>
                <button class="delete-btn" onclick="deleteHabit('${habit.id}')">
                    <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                        <polyline points="3 6 5 6 21 6"></polyline>
                        <path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"></path>
                    </svg>
                </button>
            </div>
            ${weekNav}
            ${daysTracker}
        `;
        
        container.appendChild(habitElement);
    });
}

function formatWeekRange(weekDays) {
    if (weekDays.length === 0) return '';
    const first = weekDays[0];
    const last = weekDays[6];
    return `${first.dateNumber}.${first.month} - ${last.dateNumber}.${last.month}`;
}

async function changeWeek(offset) {
    currentWeekOffset += offset;
    await renderHabits();
}

async function toggleHabitDay(habitId, date) {
    try {
        await api.habits.toggleCompletion(habitId, date);
        // Обновляем локальный кэш
        if (!habitCompletions[habitId]) {
            habitCompletions[habitId] = {};
        }
        habitCompletions[habitId][date] = !habitCompletions[habitId][date];
        await renderHabits();
    } catch (error) {
        console.error('Ошибка переключения отметки:', error);
        alert('Не удалось обновить отметку.');
    }
}

async function deleteHabit(id) {
    if (confirm('Вы уверены, что хотите удалить эту привычку?')) {
        try {
            await api.habits.delete(id);
            await loadHabits();
            await renderHabits();
        } catch (error) {
            console.error('Ошибка удаления привычки:', error);
            alert('Не удалось удалить привычку.');
        }
    }
}

async function renderWaterTracker() {
    const progressElement = document.getElementById('water-progress');
    const circlesContainer = document.getElementById('water-circles');
    const goalInput = document.getElementById('water-goal');
    const currentDateElement = document.getElementById('water-current-date');
    
    const today = new Date();
    const todayFormatted = api.formatDate(today);
    
    // Загружаем данные за сегодня
    try {
        const data = await api.habits.getWaterData(todayFormatted);
        waterAmount = data.amount || 0;
        waterGoal = data.goal || 2000;
    } catch (error) {
        console.error('Ошибка загрузки данных о воде:', error);
    }
    
    progressElement.textContent = `${waterAmount}мл / ${waterGoal}мл`;
    goalInput.value = waterGoal;
    currentDateElement.textContent = formatDisplayDate(today);
    
    circlesContainer.innerHTML = '';
    
    const totalCircles = Math.ceil(waterGoal / 100);
    const filledCircles = Math.floor(waterAmount / 100);
    
    for (let i = 0; i < totalCircles; i++) {
        const circle = document.createElement('div');
        circle.className = `water-circle ${i < filledCircles ? 'filled' : ''}`;
        
        if (i < filledCircles) {
            circle.innerHTML = `
                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <path d="m12 2.69 5.66 5.66a8 8 0 1 1-11.31 0z"></path>
                </svg>
            `;
        }
        
        circlesContainer.appendChild(circle);
    }
    
    // Рендерим календарь
    renderWaterCalendar();
}

async function addWater() {
    const today = new Date();
    const todayFormatted = api.formatDate(today);
    
    try {
        await api.habits.addWater(todayFormatted, 100);
        await renderWaterTracker();
    } catch (error) {
        console.error('Ошибка добавления воды:', error);
        alert('Не удалось добавить воду.');
    }
}

async function clearWater() {
    const today = new Date();
    const todayFormatted = api.formatDate(today);

    try {
        await api.habits.updateWaterData(todayFormatted, { amount: 0 });
        await renderWaterTracker();
    } catch (error) {
        console.error('Ошибка очистки воды:', error);
        alert('Не удалось очистить воду.');
    }
}

async function updateWaterGoal() {
    const goalInput = document.getElementById('water-goal');
    const newGoal = parseInt(goalInput.value);
    
    if (newGoal >= 100) {
        const today = new Date();
        const todayFormatted = api.formatDate(today);
        
        try {
            await api.habits.updateWaterData(todayFormatted, { goal: newGoal });
            await renderWaterTracker();
        } catch (error) {
            console.error('Ошибка обновления цели:', error);
            alert('Не удалось обновить цель.');
        }
    } else {
        alert('Цель должна быть не менее 100мл');
    }
}

function toggleWaterCalendar() {
    const calendar = document.getElementById('water-calendar');
    if (!calendar) return;
    
    if (calendar.style.display === 'none' || !calendar.style.display) {
        calendar.style.display = 'block';
        renderWaterCalendar();
    } else {
        calendar.style.display = 'none';
    }
}

async function renderWaterCalendar() {
    const calendarContainer = document.getElementById('water-calendar');
    const today = new Date();
    const currentMonth = today.getMonth();
    const currentYear = today.getFullYear();
    
    const firstDay = new Date(currentYear, currentMonth, 1);
    const lastDay = new Date(currentYear, currentMonth + 1, 0);
    const daysInMonth = lastDay.getDate();
    
    let calendarHTML = `
        <div class="calendar-header">
            <button class="nav-arrow" onclick="changeWaterMonth(-1)">
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <polyline points="15 18 9 12 15 6"></polyline>
                </svg>
            </button>
            <div class="calendar-month">${getMonthName(currentMonth)} ${currentYear}</div>
            <button class="nav-arrow" onclick="changeWaterMonth(1)">
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <polyline points="9 18 15 12 9 6"></polyline>
                </svg>
            </button>
        </div>
        <div class="calendar-grid">
            <div class="calendar-day-header">Пн</div>
            <div class="calendar-day-header">Вт</div>
            <div class="calendar-day-header">Ср</div>
            <div class="calendar-day-header">Чт</div>
            <div class="calendar-day-header">Пт</div>
            <div class="calendar-day-header">Сб</div>
            <div class="calendar-day-header">Вс</div>
    `;
    
    const startDay = firstDay.getDay() === 0 ? 6 : firstDay.getDay() - 1;
    for (let i = 0; i < startDay; i++) {
        calendarHTML += '<div class="calendar-day empty"></div>';
    }
    
    for (let day = 1; day <= daysInMonth; day++) {
        const date = new Date(currentYear, currentMonth, day);
        const dateFormatted = api.formatDate(date);
        const isToday = api.formatDate(date) === api.formatDate(today);
        
        // Загружаем данные о воде для этой даты
        let hasWater = false;
        try {
            const waterData = await api.habits.getWaterData(dateFormatted);
            hasWater = waterData.amount > 0;
        } catch (error) {
            // Игнорируем ошибки
        }
        
        calendarHTML += `
            <div class="calendar-day ${isToday ? 'today' : ''} ${hasWater ? 'has-water' : ''}" 
                 onclick="selectWaterDate('${dateFormatted}')">
                ${day}
                ${hasWater ? '<div class="water-indicator"></div>' : ''}
            </div>
        `;
    }
    
    calendarHTML += '</div>';
    calendarContainer.innerHTML = calendarHTML;
}

function getMonthName(month) {
    const months = [
        'Январь', 'Февраль', 'Март', 'Апрель', 'Май', 'Июнь',
        'Июль', 'Август', 'Сентябрь', 'Октябрь', 'Ноябрь', 'Декабрь'
    ];
    return months[month];
}

function changeWaterMonth(offset) {
    renderWaterCalendar();
}

async function selectWaterDate(date) {
    const selectedDate = new Date(date);
    const today = new Date();
    
    if (selectedDate > today) {
        alert('Нельзя выбирать будущие даты');
        return;
    }
    
    try {
        const data = await api.habits.getWaterData(date);
        waterAmount = data.amount || 0;
        waterGoal = data.goal || 2000;
        
        document.getElementById('water-current-date').textContent = formatDisplayDate(selectedDate);
        
        const circlesContainer = document.getElementById('water-circles');
        const progressElement = document.getElementById('water-progress');
        
        progressElement.textContent = `${waterAmount}мл / ${waterGoal}мл`;
        circlesContainer.innerHTML = '';
        
        const totalCircles = Math.ceil(waterGoal / 100);
        const filledCircles = Math.floor(waterAmount / 100);
        
        for (let i = 0; i < totalCircles; i++) {
            const circle = document.createElement('div');
            circle.className = `water-circle ${i < filledCircles ? 'filled' : ''}`;
            
            if (i < filledCircles) {
                circle.innerHTML = `
                    <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                        <path d="m12 2.69 5.66 5.66a8 8 0 1 1-11.31 0z"></path>
                    </svg>
                `;
            }
            
            circlesContainer.appendChild(circle);
        }
        
        document.getElementById('water-calendar').style.display = 'none';
    } catch (error) {
        console.error('Ошибка загрузки данных о воде:', error);
        alert('Не удалось загрузить данные о воде.');
    }
}

// Вспомогательная функция для экранирования HTML
function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}
