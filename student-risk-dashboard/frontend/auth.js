/**
 * Centralized Authentication Logic for Eskimo Student Risk Dashboard
 */

const AUTH_KEY = 'eskimo_auth_session';

function checkAuth() {
    const session = localStorage.getItem(AUTH_KEY);
    const currentPage = window.location.pathname.split('/').pop();

    if (!session && currentPage !== 'login.html') {
        window.location.href = 'login.html';
    } else if (session && currentPage === 'login.html') {
        window.location.href = 'index.html';
    }
}

function login(username, password) {
    const errorDisp = document.getElementById("error");
    if (username === "admin" && password === "1234") {
        localStorage.setItem(AUTH_KEY, JSON.stringify({
            user: username,
            timestamp: new Date().getTime()
        }));
        window.location.href = "index.html";
        return true;
    } else {
        if (errorDisp) {
            errorDisp.innerText = "Invalid Login";
        }
        return false;
    }
}

function logout() {
    localStorage.removeItem(AUTH_KEY);
    window.location.href = "login.html";
}

// Global exposure if needed for inline onclick handles
window.auth = {
    checkAuth,
    login,
    logout
};

// Auto-check auth on script load
document.addEventListener('DOMContentLoaded', checkAuth);
