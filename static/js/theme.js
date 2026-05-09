window.GmailCleaner = window.GmailCleaner || {};

GmailCleaner.Theme = {
    init() {
        const saved = localStorage.getItem('gmail-cleaner-theme');
        const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
        
        if (saved === 'dark' || (!saved && prefersDark)) {
            this.enableDark();
        }
    },
    
    toggle() {
        if (document.documentElement.getAttribute('data-theme') === 'dark') {
            this.disableDark();
        } else {
            this.enableDark();
        }
    },
    
    enableDark() {
        document.documentElement.setAttribute('data-theme', 'dark');
        localStorage.setItem('gmail-cleaner-theme', 'dark');
        const sun = document.querySelector('.sun-icon');
        const moon = document.querySelector('.moon-icon');
        if (sun) sun.classList.add('hidden');
        if (moon) moon.classList.remove('hidden');
    },
    
    disableDark() {
        document.documentElement.removeAttribute('data-theme');
        localStorage.setItem('gmail-cleaner-theme', 'light');
        const sun = document.querySelector('.sun-icon');
        const moon = document.querySelector('.moon-icon');
        if (sun) sun.classList.remove('hidden');
        if (moon) moon.classList.add('hidden');
    }
};

document.addEventListener('DOMContentLoaded', () => {
    GmailCleaner.Theme.init();
});
