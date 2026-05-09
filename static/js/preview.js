window.GmailCleaner = window.GmailCleaner || {};

GmailCleaner.Preview = {
    async previewSender(sender, email) {
        const modal = document.getElementById('previewModal');
        const body = document.getElementById('previewModalBody');
        const title = document.getElementById('previewModalTitle');
        const footer = document.getElementById('previewModalFooter');
        
        modal.classList.remove('hidden');
        title.textContent = `Preview: ${email}`;
        body.innerHTML = '<div class="preview-loading"><svg class="spinner" viewBox="0 0 24 24" width="32" height="32"><circle cx="12" cy="12" r="10" fill="none" stroke="currentColor" stroke-width="2" stroke-dasharray="60" stroke-linecap="round"/></svg><p>Loading emails...</p></div>';
        footer.innerHTML = '';
        
        try {
            await fetch('/api/preview-emails', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ sender: email, limit: 10 })
            });
            
            this.pollProgress();
        } catch (error) {
            body.innerHTML = `<p class="error">Error: ${error.message}</p>`;
        }
    },
    
    async pollProgress() {
        try {
            const response = await fetch('/api/preview-status');
            const status = await response.json();
            
            const body = document.getElementById('previewModalBody');
            
            if (status.loading) {
                body.innerHTML = `<div class="preview-loading"><svg class="spinner" viewBox="0 0 24 24" width="32" height="32"><circle cx="12" cy="12" r="10" fill="none" stroke="currentColor" stroke-width="2" stroke-dasharray="60" stroke-linecap="round"/></svg><p>${status.message}</p></div>`;
                setTimeout(() => this.pollProgress(), 300);
            } else if (status.done) {
                const resultsResponse = await fetch('/api/preview-results');
                const results = await resultsResponse.json();
                this.displayResults(results);
            } else if (status.error) {
                body.innerHTML = `<p class="error">Error: ${status.error}</p>`;
            }
        } catch (error) {
            setTimeout(() => this.pollProgress(), 500);
        }
    },
    
    displayResults(results) {
        const body = document.getElementById('previewModalBody');
        const footer = document.getElementById('previewModalFooter');
        
        if (!results.length) {
            body.innerHTML = '<p>No emails found.</p>';
            footer.innerHTML = '';
            return;
        }
        
        body.innerHTML = results.map(r => `
            <div class="preview-email-item">
                <div class="preview-email-header">
                    <span class="preview-email-subject">${GmailCleaner.UI.escapeHtml(r.subject)}</span>
                    <span class="preview-email-date">${GmailCleaner.UI.escapeHtml(r.date)}</span>
                </div>
                <div class="preview-email-from">From: ${GmailCleaner.UI.escapeHtml(r.from)}</div>
                <div class="preview-email-body">${GmailCleaner.UI.escapeHtml(r.body)}</div>
            </div>
        `).join('');
    },
    
    close() {
        document.getElementById('previewModal').classList.add('hidden');
    }
};
