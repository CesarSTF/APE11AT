document.getElementById('parseBtn').addEventListener('click', async () => {
    const code = document.getElementById('codeInput').value;
    const output = document.getElementById('output');

    output.textContent = 'Analizando...';
    output.className = '';

    try {
        const res = await fetch('/api/parse', {
            method: 'POST',
            body: code
        });

        const data = await res.json();
        let display = '';

        if (data.input) {
            display += 'Entrada:\n  ' + data.input + '\n\n';
        }

        if (data.tokens && data.tokens.length > 0) {
            display += 'Tokens reconocidos:\n';
            display += data.tokens.map((t, i) => {
                let arrow = (i === data.tokens.length - 1 && data.status === 'error') ? '  ← error' : '';
                return '  [' + (i + 1) + '] ' + t + arrow;
            }).join('\n');
            display += '\n\n';
        }

        if (data.status === 'ok') {
            output.className = 'success';
            display += '\u2714 ' + data.message;
            if (data.diagnostico) {
                display += '\n\n' + data.diagnostico;
            }
        } else {
            output.className = 'error';
            display += '\u2716 ' + data.message;
        }

        output.textContent = display;
    } catch (err) {
        output.className = 'error';
        output.textContent = 'Error de conexi\u00f3n: ' + err.message;
    }
});

document.getElementById('codeInput').addEventListener('keydown', (e) => {
    if (e.key === 'Enter' && e.ctrlKey) {
        document.getElementById('parseBtn').click();
    }
});
