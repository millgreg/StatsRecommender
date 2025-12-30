function switchTab(tabId) {
    document.querySelectorAll('.tab-btn').forEach(btn => btn.classList.remove('active'));
    document.querySelectorAll('.tab-content').forEach(content => content.classList.remove('active'));

    const activeBtn = Array.from(document.querySelectorAll('.tab-btn')).find(btn => btn.innerText.toLowerCase().includes(tabId.split('-')[0]));
    if (activeBtn) activeBtn.classList.add('active');
    document.getElementById(tabId).classList.add('active');
}

async function auditText() {
    const text = document.getElementById('methods-text').value;
    if (!text.trim()) {
        alert('Please paste some text first.');
        return;
    }

    showLoading(true);
    try {
        const response = await fetch('/audit_text', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ text })
        });
        const data = await response.json();
        if (data.error) throw new Error(data.error);
        displayResults(data);
    } catch (err) {
        alert('Audit failed: ' + err.message);
    } finally {
        showLoading(false);
    }
}

function showLoading(show) {
    document.getElementById('loading').classList.toggle('hidden', !show);
    document.getElementById('results').classList.toggle('hidden', show);
    if (show) document.getElementById('results').classList.add('hidden');
}

function displayResults(data) {
    const { feedback } = data;
    const resultsSection = document.getElementById('results');
    resultsSection.classList.remove('hidden');

    // Score and Rating
    const scoreElem = document.getElementById('rigor-score');
    scoreElem.innerText = feedback.overall_score.toFixed(1);

    const ratingElem = document.getElementById('rigor-rating');
    ratingElem.innerText = feedback.rigor_rating;
    ratingElem.className = 'rating-badge rating-' + feedback.rigor_rating.toLowerCase();

    // Strengths
    const strengthsList = document.getElementById('strengths-list');
    strengthsList.innerHTML = feedback.strengths.map(s => {
        const msg = typeof s === 'object' ? s.message : s;
        const ev = typeof s === 'object' && s.evidence ? s.evidence : null;
        return `
            <li>
                <div class="li-content">
                    <span class="li-msg">${msg}</span>
                    ${ev ? `<button class="evidence-btn" onclick="toggleEvidence(this)">Show Evidence</button>` : ''}
                    ${ev ? `<div class="evidence-box hidden">"${ev}"</div>` : ''}
                </div>
            </li>`;
    }).join('');

    // Gaps
    const gapsList = document.getElementById('gaps-list');
    gapsList.innerHTML = feedback.critical_gaps.map(g => {
        const msg = typeof g === 'object' ? g.message : g;
        const ev = typeof g === 'object' && g.evidence ? g.evidence : null;
        return `
            <li>
                <div class="li-content">
                    <span class="li-msg">${msg}</span>
                    ${ev ? `<button class="evidence-btn" onclick="toggleEvidence(this)">Show Evidence</button>` : ''}
                    ${ev ? `<div class="evidence-box hidden">"${ev}"</div>` : ''}
                </div>
            </li>`;
    }).join('');

    // Recommendations
    const recContainer = document.getElementById('recommendations-container');
    recContainer.innerHTML = feedback.actionable_recommendations.map(r => `
        <div class="rec-item">
            <div class="rec-header">${r.item}</div>
            <div class="rec-body">
                <div class="rec-issue">${r.issue}</div>
                <div class="rec-fix">${r.recommendation}</div>
                ${r.source_text ? `
                    <button class="evidence-btn" onclick="toggleEvidence(this)">Trace Source</button>
                    <div class="evidence-box hidden">Detection Trigger: "${r.source_text}"</div>
                ` : ''}
            </div>
        </div>
    `).join('');
}

function toggleEvidence(btn) {
    const box = btn.nextElementSibling;
    box.classList.toggle('hidden');
    btn.innerText = box.classList.contains('hidden') ? (btn.innerText.includes('Source') ? 'Trace Source' : 'Show Evidence') : 'Hide Evidence';

    // Snippet
    if (data.extracted_text_snippet) {
        document.getElementById('file-snippet').classList.remove('hidden');
        document.getElementById('text-snippet').innerText = data.extracted_text_snippet;
    } else {
        document.getElementById('file-snippet').classList.add('hidden');
    }

    window.scrollTo({ top: resultsSection.offsetTop - 50, behavior: 'smooth' });
}

// File Upload Logic
const dropZone = document.getElementById('drop-zone');
const fileInput = document.getElementById('file-upload');

dropZone.onclick = () => fileInput.click();

dropZone.ondragover = (e) => {
    e.preventDefault();
    dropZone.classList.add('dragover');
};

dropZone.ondragleave = () => dropZone.classList.remove('dragover');

dropZone.ondrop = (e) => {
    e.preventDefault();
    dropZone.classList.remove('dragover');
    if (e.dataTransfer.files.length) {
        handleFileUpload(e.dataTransfer.files[0]);
    }
};

fileInput.onchange = (e) => {
    if (e.target.files.length) {
        handleFileUpload(e.target.files[0]);
    }
};

async function handleFileUpload(file) {
    const formData = new FormData();
    formData.append('file', file);

    showLoading(true);
    try {
        const response = await fetch('/audit_file', {
            method: 'POST',
            body: formData
        });
        const data = await response.json();
        if (data.error) throw new Error(data.error);
        displayResults(data);
    } catch (err) {
        alert('File audit failed: ' + err.message);
    } finally {
        showLoading(false);
    }
}
