document.addEventListener('DOMContentLoaded', () => {
    const searchInput = document.getElementById('faq-search-input');
    const faqItems = document.querySelectorAll('.faq-item');
    const countText = document.getElementById('search-count');

    if (searchInput) {
        searchInput.addEventListener('input', (e) => {
            const term = e.target.value.toLowerCase();
            let count = 0;

            faqItems.forEach(item => {
                const text = item.innerText.toLowerCase();
                if (text.includes(term)) {
                    item.style.display = 'block';
                    count++;
                    if (term.length > 2) item.setAttribute('open', '');
                } else {
                    item.style.display = 'none';
                }
            });

            countText.innerText = term === "" 
                ? "Barcha savollar ko'rsatilmoqda" 
                : `${count} ta natija topildi`;
        });
    }
});