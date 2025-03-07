document.addEventListener('DOMContentLoaded', () => {
    const dropArea = document.getElementById('dropArea');
    const fileInput = document.getElementById('fileInput');
    const fileList = document.getElementById('fileList');
    const uploadError = document.getElementById('uploadError');
    uploadError.style.display = 'none';

    // Fix drag-and-drop
    function preventDefaults(e) {
        e.preventDefault();
        e.stopPropagation();
    }

    ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
        dropArea.addEventListener(eventName, preventDefaults);
    });

    dropArea.addEventListener('drop', handleDrop);
    dropArea.addEventListener('click', () => fileInput.click());

    function handleDrop(e) {
        const files = [...e.dataTransfer.files];
        handleFiles(files);
    }

    fileInput.addEventListener('change', () => {
        const files = [...fileInput.files];
        handleFiles(files);
        fileInput.value = ''; // Clear input to allow same file re-upload
    });

    async function handleFiles(files) {
        uploadError.textContent = '';
        
        const allowedExtensions = ['svg', 'gcode', 'png', 'jpg', 'jpeg', 'gif', 'bmp', 'webp'];
        
        for (const file of files) {
            const fileExt = file.name.split('.').pop().toLowerCase();
            
            if (!allowedExtensions.includes(fileExt)) {
                uploadError.textContent = `Formato non supportato: ${file.name}. Formati consentiti: ${allowedExtensions.join(', ')}`;
                uploadError.style.display = 'block';
                continue;
            }
    
            const formData = new FormData();
            formData.append('file', file);
    
            try {
                const response = await fetch('/upload', {
                    method: 'POST',
                    body: formData
                });
                
                if (response.ok) {
                    const data = await response.json();
                    addFileToList(data);
                } else {
                    const error = await response.json();
                    uploadError.textContent = `Errore: ${error.error}`;
                }
            } catch (err) {
                uploadError.textContent = 'Errore di connessione durante il caricamento';
            }
        }
    }

    function addFileToList(fileData) {
        const item = document.createElement('div');
        item.className = 'bg-white p-4 rounded-lg shadow-md flex items-center space-x-4';
        item.innerHTML = `
            ${fileData.preview ? 
                `<img src="${fileData.preview}" class="w-16 h-16 object-cover rounded">` :
                `<div class="w-16 h-16 bg-gray-200 flex items-center justify-center">
                    <span class="text-gray-500">${fileData.type.toUpperCase()}</span>
                </div>`
            }
            <div class="flex-1">
                <div class="font-bold">${fileData.name}</div>
                <div class="text-sm text-gray-500 status-text">Status: <span class="status">Pending</span></div>
            </div>
            <div class="flex space-x-2">
                <button class="bg-green-500 text-white px-3 py-1 rounded hover:bg-green-600 start-btn" data-filename="${fileData.name}">Start</button>
                <button class="bg-yellow-500 text-white px-3 py-1 rounded hover:bg-yellow-600 pause-btn" data-filename="${fileData.name}">Pause</button>
                <button class="bg-red-500 text-white px-3 py-1 rounded hover:bg-red-600 remove-btn" data-filename="${fileData.name}">Remove</button>
            </div>
        `;
        fileList.appendChild(item);
    }

    // Server IP Handling
    saveIpBtn.addEventListener('click', async () => {
        const ip = serverIpInput.value;
        ipError.textContent = '';
        
        const response = await fetch('/set-ip', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded'
            },
            body: `server_ip=${encodeURIComponent(ip)}`
        });
        
        if (response.ok) {
            ipError.textContent = 'IP saved successfully';
            ipError.style.color = 'green';
        } else {
            const error = await response.json();
            ipError.textContent = error.error;
        }
    });

    // File-specific Controls (Event Delegation)
    document.addEventListener('click', async (e) => {
        if (e.target.classList.contains('start-btn')) {
            const filename = e.target.dataset.filename;
            await fetch(`/file/control/start/${encodeURIComponent(filename)}`, { method: 'POST' });
        }
        if (e.target.classList.contains('pause-btn')) {
            const filename = e.target.dataset.filename;
            await fetch(`/file/control/pause/${encodeURIComponent(filename)}`, { method: 'POST' });
        }
        if (e.target.classList.contains('remove-btn')) {
            const filename = e.target.dataset.filename;
            await fetch(`/file/control/remove/${encodeURIComponent(filename)}`, { method: 'POST' });
        }
    });

    // Polling Queue Status
    async function updateQueueStatus() {
        const response = await fetch('/queue/status');
        const data = await response.json();
        
        data.queue.forEach(file => {
            const fileElement = document.querySelector(`[data-filename="${file.name}"]`).closest('.bg-white');
            if (fileElement) {
                const statusText = fileElement.querySelector('.status');
                statusText.textContent = file.status;
                
                // Update button states
                const startBtn = fileElement.querySelector('.start-btn');
                const pauseBtn = fileElement.querySelector('.pause-btn');
                
                if (file.status === 'Processing') {
                    startBtn.disabled = true;
                    pauseBtn.disabled = false;
                } else {
                    startBtn.disabled = false;
                    pauseBtn.disabled = true;
                }
            }
        });
    }

    setInterval(updateQueueStatus, 2000);
});
