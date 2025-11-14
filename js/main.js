// Главная страница - простой скрипт для инициализации
document.addEventListener('DOMContentLoaded', function() {
    console.log('MaxPersonalEffect - Главная страница загружена');
    
    // Добавляем анимацию при загрузке карточек
    const cards = document.querySelectorAll('.section-card');
    cards.forEach((card, index) => {
        card.style.opacity = '0';
        card.style.transform = 'translateY(20px)';
        
        setTimeout(() => {
            card.style.transition = 'all 0.5s ease';
            card.style.opacity = '1';
            card.style.transform = 'translateY(0)';
        }, index * 100);
    });
    
    // Добавляем интерактивность для карточек
    cards.forEach(card => {
        card.addEventListener('mouseenter', function() {
            this.style.transform = 'translateY(-5px) scale(1.02)';
        });
        
        card.addEventListener('mouseleave', function() {
            this.style.transform = 'translateY(0) scale(1)';
        });
    });
});