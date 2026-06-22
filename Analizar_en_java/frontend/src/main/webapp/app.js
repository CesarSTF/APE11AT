const BACKENDS = {
    java: { port: 8080, label: 'Java' },
    python: { port: 8081, label: 'Python' }
};

let activeBackend = 'java';

const backendSelect = document.getElementById('backendSelect');
const backendStatus = document.getElementById('backendStatus');
const codeInput = document.getElementById('codeInput');
const output = document.getElementById('output');
const parseBtn = document.getElementById('parseBtn');

function apiUrl() {
    const be = BACKENDS[activeBackend];
    return `http://localhost:${be.port}/api/parse`;
}

async function checkBackend(backend) {
    const be = BACKENDS[backend];
    try {
        const res = await fetch(`http://localhost:${be.port}/api/parse`, {
            method: 'POST',
            body: 'x = 1'
        });
        if (res.ok) return true;
    } catch (_) {}
    return false;
}

async function updateStatus() {
    backendStatus.textContent = '● verificando...';
    backendStatus.className = 'status-badge checking';
    const ok = await checkBackend(activeBackend);
    if (ok) {
        backendStatus.textContent = `● ${BACKENDS[activeBackend].label} conectado`;
        backendStatus.className = 'status-badge online';
    } else {
        backendStatus.textContent = `● ${BACKENDS[activeBackend].label} desconectado`;
        backendStatus.className = 'status-badge offline';
    }
}

backendSelect.addEventListener('change', () => {
    activeBackend = backendSelect.value;
    updateStatus();
});

parseBtn.addEventListener('click', async () => {
    const code = codeInput.value;

    output.innerHTML = '<p>Analizando...</p>';
    output.className = '';

    const ok = await checkBackend(activeBackend);
    if (!ok) {
        output.className = 'error';
        output.innerHTML = `<div class="msg">✖ ${BACKENDS[activeBackend].label} no esta disponible en localhost:${BACKENDS[activeBackend].port}</div>`;
        updateStatus();
        return;
    }

    try {
        const res = await fetch(apiUrl(), {
            method: 'POST',
            body: code
        });

        const data = await res.json();
        let html = '';

        if (data.input) {
            html += `<div class="info-block"><strong>Entrada:</strong> <code>${escapeHtml(data.input)}</code></div>`;
        }

        if (data.tokens && data.tokens.length > 0) {
            html += '<table class="token-table">';
            html += '<thead><tr><th>#</th><th>Token</th><th>Lexema</th><th>IDENTIFICADO</th></tr></thead>';
            html += '<tbody>';
            data.tokens.forEach((t, i) => {
                const rowClass = t.identificado === 'NO IDENTIFICADO' ? ' class="error-row"' : '';
                const statusIcon = t.identificado === 'NO IDENTIFICADO' ? '\u2716' : '\u2714';
                html += `<tr${rowClass}>`
                    + `<td>${i + 1}</td>`
                    + `<td>${escapeHtml(t.token)}</td>`
                    + `<td>${escapeHtml(t.lexema)}</td>`
                    + `<td>${statusIcon} ${escapeHtml(t.identificado)}</td>`
                    + '</tr>';
            });
            html += '</tbody></table>';
        }

        if (data.status === 'ok') {
            output.className = 'success';
            html += `<div class="msg">\u2714 ${escapeHtml(data.message)}</div>`;
            if (data.diagnostico) {
                html += `<div class="diag">${escapeHtml(data.diagnostico)}</div>`;
            }
        } else {
            output.className = 'error';
            html += `<div class="msg">\u2716 ${escapeHtml(data.message)}</div>`;
        }

        output.innerHTML = html;
    } catch (err) {
        output.className = 'error';
        output.innerHTML = `<div class="msg">Error de conexi\u00f3n: ${escapeHtml(err.message)}</div>`;
    }
});

codeInput.addEventListener('keydown', (e) => {
    if (e.key === 'Enter' && e.ctrlKey) {
        parseBtn.click();
    }
});

function escapeHtml(str) {
    const div = document.createElement('div');
    div.textContent = str;
    return div.innerHTML;
}

updateStatus();
setInterval(updateStatus, 5000);
