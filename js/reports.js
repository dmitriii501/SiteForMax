// Отчёты и аналитика
document.addEventListener('DOMContentLoaded', async function() {
    await updateReports();
});

async function updateReports() {
    try {
        await updateStats();
        await updateTaskChart();
        await updateMoodChart();
        await updateHabitsProgress();
        await updateEmotionsChart();
        await updateInsights();
    } catch (error) {
        console.error('Ошибка обновления отчётов:', error);
    }
}

async function updateStats() {
    try {
        const stats = await api.reports.getStats();
        
        document.getElementById('completion-rate').textContent = `${stats.completion_rate}%`;
        document.getElementById('tasks-completed').textContent = stats.tasks_completed_7days;
        document.getElementById('avg-mood').textContent = `${stats.avg_mood_7days}/5`;
        document.getElementById('streak-days').textContent = stats.streak_days;
    } catch (error) {
        console.error('Ошибка загрузки статистики:', error);
    }
}

async function updateTaskChart() {
    try {
        const taskData = await api.reports.getTasksChart();
        const chart = document.getElementById('tasks-chart');
        
        let chartHTML = '';
        const maxTotal = Math.max(...taskData.map(d => d.total), 1);
        
        taskData.forEach(data => {
            const completedHeight = (data.completed / maxTotal) * 100;
            const totalHeight = (data.total / maxTotal) * 100;
            
            chartHTML += `
                <div style="display: flex; flex-direction: column; align-items: center; height: 100%; flex: 1;">
                    <div style="display: flex; flex-direction: column; justify-content: flex-end; height: 100%; width: 30px; position: relative;">
                        <div style="height: ${totalHeight}%; background-color: #e9d5ff; border-radius: 4px 4px 0 0; margin-bottom: 2px;"></div>
                        <div style="height: ${completedHeight}%; background-color: #8b5cf6; border-radius: 4px 4px 0 0; position: absolute; bottom: 0; width: 100%;"></div>
                    </div>
                    <div style="font-size: 12px; color: #6b7280; margin-top: 8px;">${data.day}</div>
                </div>
            `;
        });
        
        chart.innerHTML = chartHTML;
    } catch (error) {
        console.error('Ошибка загрузки графика задач:', error);
    }
}

async function updateMoodChart() {
    try {
        const moodData = await api.reports.getMoodChart();
        const chart = document.getElementById('mood-chart');
        
        const svgWidth = 400;
        const svgHeight = 150;
        const padding = { top: 20, right: 30, bottom: 40, left: 30 };
        
        const chartWidth = svgWidth - padding.left - padding.right;
        const chartHeight = svgHeight - padding.top - padding.bottom;

        let svgHTML = `
            <svg width="100%" height="${svgHeight}" viewBox="0 0 ${svgWidth} ${svgHeight}">
        `;

        for (let i = 0; i < moodData.length - 1; i++) {
            const current = moodData[i];
            const next = moodData[i + 1];
            
            if (current.mood !== null && current.mood > 0 && next.mood !== null && next.mood > 0) {
                const x1 = padding.left + (i / (moodData.length - 1)) * chartWidth;
                const x2 = padding.left + ((i + 1) / (moodData.length - 1)) * chartWidth;
                
                const y1 = padding.top + chartHeight - ((current.mood - 1) / 4) * chartHeight;
                const y2 = padding.top + chartHeight - ((next.mood - 1) / 4) * chartHeight;
                
                svgHTML += `
                    <line x1="${x1}" y1="${y1}" x2="${x2}" y2="${y2}" 
                          stroke="#ec4899" stroke-width="2" fill="none" />
                `;
            }
        }

        moodData.forEach((data, index) => {
            if (data.mood !== null && data.mood > 0) {
                const x = padding.left + (index / (moodData.length - 1)) * chartWidth;
                const y = padding.top + chartHeight - ((data.mood - 1) / 4) * chartHeight;
                
                svgHTML += `
                    <circle cx="${x}" cy="${y}" r="4" fill="#ec4899" stroke="white" stroke-width="2" />
                `;
            }
        });

        moodData.forEach((data, index) => {
            const x = padding.left + (index / (moodData.length - 1)) * chartWidth;
            const y = svgHeight - 10;
            
            svgHTML += `
                <text x="${x}" y="${y}" text-anchor="middle" font-size="12" fill="${data.mood !== null && data.mood > 0 ? '#6b7280' : '#9ca3af'}" font-family="Inter, sans-serif">
                    ${data.day}
                </text>
            `;
        });

        for (let mood = 1; mood <= 5; mood++) {
            const y = padding.top + chartHeight - ((mood - 1) / 4) * chartHeight;
            svgHTML += `
                <text x="${padding.left - 10}" y="${y + 4}" text-anchor="end" font-size="11" fill="#9ca3af" font-family="Inter, sans-serif">
                    ${mood}
                </text>
            `;
        }

        svgHTML += '</svg>';
        chart.innerHTML = svgHTML;
    } catch (error) {
        console.error('Ошибка загрузки графика настроения:', error);
    }
}

async function updateHabitsProgress() {
    try {
        const progressData = await api.reports.getHabitsProgress();
        const container = document.getElementById('habits-progress');
        
        let progressHTML = '';
        
        progressData.forEach(habit => {
            progressHTML += `
                <div class="habit-progress-item">
                    <div class="habit-name">${escapeHtml(habit.habit_name)}</div>
                    <div class="habit-progress-bar">
                        <div class="habit-progress-fill" style="width: ${habit.progress}%; background-color: #8b5cf6;"></div>
                    </div>
                    <div class="habit-percentage">${habit.progress}%</div>
                </div>
            `;
        });
        
        // Добавляем потребление воды
        const today = new Date();
        const todayFormatted = api.formatDate(today);
        try {
            const waterData = await api.habits.getWaterData(todayFormatted);
            const waterProgress = Math.round((waterData.amount / waterData.goal) * 100);
            
            progressHTML += `
                <div class="habit-progress-item">
                    <div class="habit-name">Потребление воды</div>
                    <div class="habit-progress-bar">
                        <div class="habit-progress-fill" style="width: ${waterProgress}%; background-color: #3b82f6;"></div>
                    </div>
                    <div class="habit-percentage">${waterProgress}%</div>
                </div>
            `;
        } catch (error) {
            // Игнорируем ошибку
        }
        
        container.innerHTML = progressHTML;
    } catch (error) {
        console.error('Ошибка загрузки прогресса привычек:', error);
    }
}

async function updateEmotionsChart() {
    try {
        const emotionsData = await api.reports.getEmotionsChart();
        const container = document.getElementById('emotions-chart');
        
        let chartHTML = '';
        
        const colors = ['#8b5cf6', '#ec4899', '#10b981', '#f59e0b', '#3b82f6'];
        
        emotionsData.forEach((emotion, index) => {
            chartHTML += `
                <div class="emotion-chart-item">
                    <div class="emotion-color" style="background-color: ${colors[index] || '#6b7280'};"></div>
                    <span>${escapeHtml(emotion.emotion)} ${emotion.percentage}%</span>
                </div>
            `;
        });
        
        if (emotionsData.length === 0) {
            chartHTML = '<div class="empty-state">Нет данных об эмоциях за эту неделю</div>';
        }
        
        container.innerHTML = chartHTML;
    } catch (error) {
        console.error('Ошибка загрузки графика эмоций:', error);
    }
}

async function updateInsights() {
    try {
        const stats = await api.reports.getStats();
        const weeklyReport = await api.reports.getWeeklyReport();
        
        document.getElementById('insight-completion').textContent = `${stats.completion_rate}%`;
        document.getElementById('insight-streak').textContent = `${stats.streak_days}-дневную`;
        
        const today = new Date();
        const todayFormatted = api.formatDate(today);
        try {
            const waterData = await api.habits.getWaterData(todayFormatted);
            const waterProgress = Math.round((waterData.amount / waterData.goal) * 100);
            document.getElementById('insight-water').textContent = `${waterProgress}%`;
        } catch (error) {
            document.getElementById('insight-water').textContent = '0%';
        }
    } catch (error) {
        console.error('Ошибка загрузки инсайтов:', error);
    }
}

// Вспомогательная функция для экранирования HTML
function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}
