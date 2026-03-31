async function fetchJSON(url, options) {
  const response = await fetch(url, options);
  if (!response.ok) {
    const text = await response.text();
    throw new Error(text || 'Erro na requisição');
  }
  return response.json();
}

function setMessage(message, isError = false) {
  const box = document.getElementById('messageBox');
  box.textContent = message;
  box.style.color = isError ? '#ff8e8e' : '#a7ff00';
}

function renderPreview(imageName) {
  const preview = document.getElementById('previewBox');
  preview.innerHTML = imageName ? `<img src="/data-images/${encodeURIComponent(imageName)}" onerror="this.remove()" alt="Prévia" />` : '';
}

async function loadAssets() {
  const [assets, docs, images, history] = await Promise.all([
    fetchJSON('/api/assets'),
    fetchJSON('/api/documents'),
    fetchJSON('/api/images'),
    fetchJSON('/api/history')
  ]);

  document.getElementById('metricDocs').textContent = docs.length;
  document.getElementById('metricImages').textContent = images.length;

  const docsList = document.getElementById('docsList');
  docsList.innerHTML = docs.map(d => `<li>${d.name}</li>`).join('');

  const select = document.getElementById('imageSelect');
  select.innerHTML = images.map(img => `<option value="${img.name}">${img.name}</option>`).join('');
  select.onchange = () => renderPreview(select.value);
  if (images.length) renderPreview(images[0].name);

  const historyTable = document.getElementById('historyTable');
  if (!history.length) {
    historyTable.innerHTML = '<p>Nenhuma análise salva ainda.</p>';
  } else {
    historyTable.innerHTML = `
      <table class="table">
        <thead>
          <tr><th>ID</th><th>Empresa</th><th>Imagem</th><th>Pessoas</th><th>Regras</th><th>Data</th></tr>
        </thead>
        <tbody>
          ${history.map(row => `<tr><td>${row.id}</td><td>${row.company}</td><td>${row.image_name}</td><td>${row.people_count}</td><td>${row.rules_count}</td><td>${row.created_at || ''}</td></tr>`).join('')}
        </tbody>
      </table>
    `;
  }
}

document.getElementById('analyzeForm').addEventListener('submit', async (event) => {
  event.preventDefault();
  const formData = new FormData(event.target);
  try {
    const result = await fetchJSON('/api/analyze', { method: 'POST', body: formData });
    document.getElementById('resultBox').textContent = JSON.stringify(result, null, 2);
    document.getElementById('metricPeople').textContent = result.people_count;
    document.getElementById('metricRules').textContent = result.rules_count;
    setMessage('Análise concluída com sucesso.');
    await loadAssets();
  } catch (error) {
    setMessage(error.message, true);
  }
});

document.getElementById('uploadDocForm').addEventListener('submit', async (event) => {
  event.preventDefault();
  try {
    const formData = new FormData(event.target);
    await fetchJSON('/api/upload/document', { method: 'POST', body: formData });
    setMessage('Documento enviado com sucesso. Agora reindexe a base.');
    event.target.reset();
    await loadAssets();
  } catch (error) {
    setMessage(error.message, true);
  }
});

document.getElementById('uploadImgForm').addEventListener('submit', async (event) => {
  event.preventDefault();
  try {
    const formData = new FormData(event.target);
    await fetchJSON('/api/upload/image', { method: 'POST', body: formData });
    setMessage('Imagem enviada com sucesso.');
    event.target.reset();
    await loadAssets();
  } catch (error) {
    setMessage(error.message, true);
  }
});

document.getElementById('reindexBtn').addEventListener('click', async () => {
  try {
    const result = await fetchJSON('/api/reindex', { method: 'POST' });
    setMessage(`Índice reconstruído: ${result.documents} documentos e ${result.chunks} chunks.`);
    await loadAssets();
  } catch (error) {
    setMessage(error.message, true);
  }
});

loadAssets().catch(error => setMessage(error.message, true));
