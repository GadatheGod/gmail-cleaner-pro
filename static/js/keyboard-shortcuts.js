window.GmailCleaner = window.GmailCleaner || {};

GmailCleaner.KeyboardShortcuts = {
    setup() {
        document.addEventListener('keydown', (e) => {
            // Don't trigger shortcuts when typing in input/textarea
            if (e.target.tagName === 'INPUT' || e.target.tagName === 'TEXTAREA' || e.target.tagName === 'SELECT') return;
            
            // Ctrl/Cmd + key combinations
            if (e.ctrlKey || e.metaKey) {
                switch(e.key.toLowerCase()) {
                    case '1': e.preventDefault(); GmailCleaner.UI.showView('unsubscribe'); break;
                    case '2': e.preventDefault(); GmailCleaner.UI.showView('delete'); break;
                    case '3': e.preventDefault(); GmailCleaner.UI.showView('markread'); break;
                    case 'k': e.preventDefault(); GmailCleaner.Filters.showBar(!document.getElementById('filterBar')?.classList.contains('hidden')); break;
                    case 's': e.preventDefault(); GmailCleaner.Scanner.startScan(); break;
                    case 'a': e.preventDefault(); this.selectAll(); break;
                }
            }
            
            // Single key shortcuts
            switch(e.key.toLowerCase()) {
                case 'escape': GmailCleaner.Filters.clear(); break;
            }
        });
    },
    
    selectAll() {
        const currentView = GmailCleaner.currentView;
        if (currentView === 'unsubscribe') {
            document.getElementById('selectAll').checked = true;
            GmailCleaner.Scanner.toggleSelectAll();
        } else if (currentView === 'delete') {
            document.getElementById('deleteSelectAll').checked = true;
            GmailCleaner.Delete.toggleSelectAll();
        }
    }
};

// Initialize on DOM load
document.addEventListener('DOMContentLoaded', () => {
    GmailCleaner.KeyboardShortcuts.setup();
});
