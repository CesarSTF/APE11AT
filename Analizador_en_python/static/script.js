function solve() {
    const eq1 = document.getElementById('eq1').value.trim();
    const eq2 = document.getElementById('eq2').value.trim();
    const resultDiv = document.getElementById('result');
    const conclusionDiv = document.getElementById('conclusion');
    const loading = document.getElementById('loading');

    resultDiv.style.display = 'none';
    conclusionDiv.style.display = 'none';
    loading.style.display = 'block';

    fetch('/solve', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ eq1, eq2 })
    })
    .then(r => r.json())
    .then(data => {
        loading.style.display = 'none';
        resultDiv.style.display = 'block';
        resultDiv.className = data.status === 'success' ? 'success' : 'error';

        if (data.status === 'success') {
            resultDiv.innerHTML = `
                <div class="solution"><strong>x</strong> = ${data.x}</div>
                <div class="solution"><strong>y</strong> = ${data.y}</div>
                <ul class="steps">${data.pasos.map(p => `<li>${p}</li>`).join('')}</ul>
            `;
            conclusionDiv.style.display = 'block';
            const isEntero = Number.isInteger(Number(data.x)) && Number.isInteger(Number(data.y));
            const cx = isEntero ? data.x : Math.round(data.x);
            const cy = isEntero ? data.y : Math.round(data.y);
            conclusionDiv.innerHTML = `
                <strong>Conclusión</strong><br>
                Cuadernos vendidos (x): <span class="conclusion-value">${cx}</span><br>
                Lápices vendidos (y): <span class="conclusion-value">${cy}</span>
            `;
        } else {
            resultDiv.textContent = data.msg;
            conclusionDiv.style.display = 'none';
        }
    })
    .catch(() => {
        loading.style.display = 'none';
        resultDiv.style.display = 'block';
        resultDiv.className = 'error';
        resultDiv.textContent = 'Error de conexión.';
        conclusionDiv.style.display = 'none';
    });
}

document.addEventListener('keydown', e => {
    if (e.key === 'Enter') solve();
});
