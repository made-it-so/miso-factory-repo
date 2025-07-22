async function authorizedFetch(url, options = {}) {
    const token = localStorage.getItem('miso_token');
    if (!token) { window.location.href = '/login.html'; return; }
    const headers = { ...options.headers, 'Authorization': `Bearer ${token}` };
    const api_url = `/api${url}`;
    const response = await fetch(api_url, { ...options, headers });
    if (response.status === 401) {
        localStorage.removeItem('miso_token');
        window.location.href = '/login.html';
    }
    return response;
}
if (window.location.pathname.includes('index.html') || window.location.pathname === '/') {
    if (!localStorage.getItem('miso_token')) { window.location.href = '/login.html'; }
    const getInfoButton = document.getElementById('getInfoButton');
    const responseOutput = document.getElementById('responseOutput');
    const logoutButton = document.getElementById('logoutButton');
    getInfoButton.addEventListener('click', async () => {
        responseOutput.textContent = 'Dispatching get_info task...';
        const payload = { task: 'get_info' };
        try {
            const response = await authorizedFetch('/dispatch', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(payload)
            });
            const data = await response.json();
            if (!response.ok) { throw new Error(data.message || data.error || 'API Error'); }
            responseOutput.textContent = JSON.stringify(data, null, 2);
        } catch (error) { responseOutput.textContent = `Error: ${error.message}`; }
    });
    logoutButton.addEventListener('click', () => {
        localStorage.removeItem('miso_token');
        window.location.href = '/login.html';
    });
}
if (window.location.pathname.includes('login.html')) {
    const loginForm = document.getElementById('loginForm');
    loginForm.addEventListener('submit', async (event) => {
        event.preventDefault();
        const errorMsg = document.getElementById('errorMsg');
        errorMsg.textContent = '';
        const username = loginForm.username.value;
        const password = loginForm.password.value;
        try {
            const response = await fetch('/api/login', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ username, password })
            });
            const data = await response.json();
            if (!response.ok) { throw new Error(data.message || 'Login failed'); }
            localStorage.setItem('miso_token', data.token);
            window.location.href = '/index.html';
        } catch (error) { errorMsg.textContent = error.message; }
    });
}
