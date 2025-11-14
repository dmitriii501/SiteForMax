// Трекер настроения
let moodEntries = [];
let selectedDate = new Date();
let selectedEmotions = [];
let selectedMood = null;

document.addEventListener('DOMContentLoaded', async function() {
    await loadMoodEntries();
    setupEventListeners();
    await initializeMoodCalendar();
    initializeEmotions();
    updateCurrentDate();
    updateMoodUI();
});

function setupEventListeners() {
    document.querySelectorAll('.mood-option').forEach(option => {
        option.addEventListener('click', selectMood);
    });
}

async function loadMoodEntries() {
    try {
        moodEntries = await api.mood.getAll();
    } catch (error) {
        console.error('Ошибка загрузки записей настроения:', error);
        moodEntries = [];
    }
}

function updateCurrentDate() {
    const dateElement = document.getElementById('current-date');
    const options = { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' };
    dateElement.textContent = selectedDate.toLocaleDateString('ru-RU', options);
}

async function initializeMoodCalendar() {
    const calendar = document.getElementById('mood-calendar');
    
    const dayNames = ['Пн', 'Вт', 'Ср', 'Чт', 'Пт', 'Сб', 'Вс'];
    
    let calendarHTML = `
        <div class="calendar-header">
            ${dayNames.map(day => `<div>${day}</div>`).join('')}
        </div>
        <div class="calendar-grid">
    `;
    
    const year = selectedDate.getFullYear();
    const month = selectedDate.getMonth();
    const firstDay = new Date(year, month, 1);
    const lastDay = new Date(year, month + 1, 0);
    const daysInMonth = lastDay.getDate();
    
    const todayStr = api.formatDate(new Date());
    const selectedDateStr = api.formatDate(selectedDate);
    
    for (let i = 0; i < firstDay.getDay(); i++) {
        calendarHTML += `<div class="calendar-day empty"></div>`;
    }
    
    for (let i = 1; i <= daysInMonth; i++) {
        const dateStr = `${year}-${String(month + 1).padStart(2, '0')}-${String(i).padStart(2, '0')}`;
        const moodEntry = moodEntries.find(entry => entry.date === dateStr);
        
        const isToday = dateStr === todayStr;
        const isSelected = dateStr === selectedDateStr;
        
        let moodClass = '';
        if (moodEntry && moodEntry.mood) {
            moodClass = `mood-${moodEntry.mood}`;
        }
        
        calendarHTML += `
            <div class="calendar-day ${isToday ? 'today' : ''} ${moodClass} ${isSelected ? 'selected' : ''}" 
                 onclick="selectCalendarDate('${dateStr}')">
                ${i}
            </div>
        `;
    }
    
    calendarHTML += '</div>';
    calendar.innerHTML = calendarHTML;
}

async function selectCalendarDate(dateStr) {
    const clickedDate = new Date(dateStr);
    const selectedDay = document.querySelector(`.calendar-day[onclick="selectCalendarDate('${dateStr}')"]`);
    
    if (api.formatDate(selectedDate) === dateStr && selectedDay.classList.contains('selected')) {
        selectedDay.classList.remove('selected');
        selectedDate = new Date();
        updateCurrentDate();
        
        selectedMood = null;
        selectedEmotions = [];
        
        updateMoodSelection();
        updateEmotionsUI();
        updateMoodSummary();
        return;
    }
    
    document.querySelectorAll('.calendar-day').forEach(day => {
        day.classList.remove('selected');
    });
    
    if (selectedDay) {
        selectedDay.classList.add('selected');
    }
    
    selectedDate = clickedDate;
    updateCurrentDate();
    
    // Загружаем данные для выбранной даты
    try {
        const moodEntry = await api.mood.getByDate(dateStr);
        if (moodEntry) {
            selectedMood = moodEntry.mood;
            selectedEmotions = [...(moodEntry.emotions || [])];
        } else {
            selectedMood = null;
            selectedEmotions = [];
        }
    } catch (error) {
        // Если записи нет, это нормально
        selectedMood = null;
        selectedEmotions = [];
    }
    
    updateMoodSelection();
    updateEmotionsUI();
    updateMoodSummary();
}

function updateMoodSelection() {
    document.querySelectorAll('.mood-option').forEach(option => {
        option.classList.remove('selected');
    });
    
    if (selectedMood) {
        const selectedOption = document.querySelector(`.mood-option[data-value="${selectedMood}"]`);
        if (selectedOption) {
            selectedOption.classList.add('selected');
        }
    }
}

function initializeEmotions() {
    const emotions = [
        'Счастливый', 'Грустный', 'Тревожный', 'Спокойный', 'Мотивированный', 'Уставший',
        'Энергичный', 'Раздражённый', 'Умиротворённый', 'Напряжённый', 'Вдохновлённый', 'Злой',
        'Смущённый', 'Одинокий', 'Уверенный', 'Перегруженный', 'Игривый', 'Раздосадованный',
        'Испуганный', 'Апатичный'
    ];
    
    const container = document.getElementById('emotions-grid');
    
    emotions.forEach(emotion => {
        const button = document.createElement('button');
        button.className = 'emotion-tag';
        button.textContent = emotion;
        button.addEventListener('click', () => toggleEmotion(emotion));
        container.appendChild(button);
    });
}

async function selectMood(event) {
    const moodValue = parseInt(event.currentTarget.getAttribute('data-value'));
    
    document.querySelectorAll('.mood-option').forEach(option => {
        option.classList.remove('selected');
    });
    
    event.currentTarget.classList.add('selected');
    
    selectedMood = moodValue;
    await saveMoodEntry();
    updateMoodSummary();
}

async function toggleEmotion(emotion) {
    const emotionIndex = selectedEmotions.indexOf(emotion);
    
    if (emotionIndex === -1) {
        selectedEmotions.push(emotion);
    } else {
        selectedEmotions.splice(emotionIndex, 1);
    }
    
    await saveMoodEntry();
    updateEmotionsUI();
    updateMoodSummary();
}

async function saveMoodEntry() {
    const dateStr = api.formatDate(selectedDate);
    
    try {
        if (selectedMood !== null || selectedEmotions.length > 0) {
            await api.mood.createOrUpdate(dateStr, {
                mood: selectedMood,
                emotions: selectedEmotions
            });
            await loadMoodEntries();
            await initializeMoodCalendar();
        } else {
            // Удаляем запись, если нет настроения и эмоций
            try {
                await api.mood.delete(dateStr);
                await loadMoodEntries();
                await initializeMoodCalendar();
            } catch (error) {
                // Игнорируем ошибку, если записи нет
            }
        }
    } catch (error) {
        console.error('Ошибка сохранения записи настроения:', error);
        alert('Не удалось сохранить запись настроения.');
    }
}

function updateEmotionsUI() {
    document.querySelectorAll('.emotion-tag').forEach(button => {
        if (selectedEmotions.includes(button.textContent)) {
            button.classList.add('selected');
        } else {
            button.classList.remove('selected');
        }
    });
    
    const emotionsList = document.getElementById('emotions-list');
    emotionsList.textContent = selectedEmotions.join(', ');
}

function updateMoodSummary() {
    const summaryMood = document.getElementById('summary-mood');
    const summaryEmotionsCount = document.getElementById('summary-emotions-count');
    const moodSummary = document.getElementById('mood-summary');
    
    if (selectedMood !== null || selectedEmotions.length > 0) {
        moodSummary.style.display = 'block';
        
        const moodLabels = {
            1: '😢 Очень плохо',
            2: '😟 Плохо',
            3: '😐 Нормально',
            4: '😊 Хорошо',
            5: '😄 Отлично'
        };
        
        summaryMood.textContent = selectedMood ? moodLabels[selectedMood] : '-';
        summaryEmotionsCount.textContent = selectedEmotions.length;
        
        addDeleteButton();
    } else {
        moodSummary.style.display = 'none';
    }
}

function addDeleteButton() {
    const moodSummary = document.getElementById('mood-summary');
    
    const oldButton = document.getElementById('delete-mood-entry');
    if (oldButton) {
        oldButton.remove();
    }
    
    const deleteButton = document.createElement('button');
    deleteButton.id = 'delete-mood-entry';
    deleteButton.className = 'btn-outline delete-mood-btn';
    deleteButton.innerHTML = `
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <polyline points="3 6 5 6 21 6"></polyline>
            <path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"></path>
        </svg>
        Удалить запись
    `;
    deleteButton.onclick = deleteMoodEntry;
    
    moodSummary.appendChild(deleteButton);
}

async function deleteMoodEntry() {
    const dateStr = api.formatDate(selectedDate);
    
    try {
        await api.mood.delete(dateStr);
        
        selectedMood = null;
        selectedEmotions = [];
        
        await loadMoodEntries();
        
        updateMoodSelection();
        updateEmotionsUI();
        updateMoodSummary();
        await initializeMoodCalendar();
    } catch (error) {
        console.error('Ошибка удаления записи:', error);
        alert('Не удалось удалить запись.');
    }
}

function updateMoodUI() {
    updateCurrentDate();
    updateMoodSelection();
    updateEmotionsUI();
    updateMoodSummary();
}
