// Auth gate + session helpers (loaded before app.js)
const API_BASE = 'http://localhost:8000';
const AUTH_STORAGE_KEY = 'reviewer_auth';

const Auth = (() => {
    let session = null; // { access_token, refresh_token, user }
    let onAuthenticated = null;
    let onSignedOut = null;

    const loginView = () => document.getElementById('loginView');
    const appView = () => document.getElementById('appView');
    const authEmail = () => document.getElementById('authEmail');
    const authPassword = () => document.getElementById('authPassword');
    const authMessage = () => document.getElementById('authMessage');
    const authUserEmail = () => document.getElementById('authUserEmail');

    function setMessage(text, isError = false) {
        const el = authMessage();
        if (!el) return;
        el.textContent = text || '';
        el.classList.toggle('error', Boolean(isError && text));
    }

    function restoreSession() {
        try {
            const raw = localStorage.getItem(AUTH_STORAGE_KEY);
            session = raw ? JSON.parse(raw) : null;
        } catch (e) {
            session = null;
            localStorage.removeItem(AUTH_STORAGE_KEY);
        }
        return session;
    }

    function persistSession(next) {
        session = next;
        if (session) {
            localStorage.setItem(AUTH_STORAGE_KEY, JSON.stringify(session));
        } else {
            localStorage.removeItem(AUTH_STORAGE_KEY);
        }
    }

    function getSession() {
        return session;
    }

    function isLoggedIn() {
        return Boolean(session?.access_token && session?.user);
    }

    function authHeaders() {
        if (!session?.access_token) return {};
        return { Authorization: `Bearer ${session.access_token}` };
    }

    async function apiJson(path, options = {}) {
        const headers = {
            'Content-Type': 'application/json',
            ...(options.headers || {}),
            ...authHeaders(),
        };
        const response = await fetch(`${API_BASE}${path}`, { ...options, headers });
        let data = null;
        try {
            data = await response.json();
        } catch (e) {
            data = null;
        }
        if (!response.ok) {
            const detail = data?.detail;
            const message = typeof detail === 'string'
                ? detail
                : (Array.isArray(detail) ? detail.map(d => d.msg).join(', ') : `Request failed (${response.status})`);
            throw new Error(message);
        }
        return data;
    }

    function showLogin() {
        loginView()?.classList.remove('hidden');
        appView()?.classList.add('hidden');
    }

    function showApp() {
        loginView()?.classList.add('hidden');
        appView()?.classList.remove('hidden');
        if (authUserEmail() && session?.user) {
            authUserEmail().textContent = session.user.email || '';
        }
    }

    async function enterApp() {
        showApp();
        if (typeof onAuthenticated === 'function') {
            await onAuthenticated(session);
        }
    }

    async function refreshMe() {
        if (!session?.access_token) return false;
        try {
            const data = await apiJson('/api/auth/me');
            session.user = data.user;
            persistSession(session);
            return true;
        } catch (e) {
            console.warn('Session expired:', e.message);
            persistSession(null);
            return false;
        }
    }

    async function signUp() {
        const email = authEmail().value.trim();
        const password = authPassword().value;
        if (!email || password.length < 6) {
            setMessage('Enter email and a password of at least 6 characters.', true);
            return;
        }
        setMessage('Creating account...');
        try {
            const data = await apiJson('/api/auth/signup', {
                method: 'POST',
                body: JSON.stringify({ email, password }),
            });
            if (data.needs_email_confirmation) {
                persistSession(null);
                setMessage(data.message || 'Confirm your email, then sign in.');
                return;
            }
            persistSession({
                access_token: data.access_token,
                refresh_token: data.refresh_token,
                user: data.user,
            });
            authPassword().value = '';
            setMessage('');
            await enterApp();
        } catch (e) {
            setMessage(e.message, true);
        }
    }

    async function signIn() {
        const email = authEmail().value.trim();
        const password = authPassword().value;
        if (!email || !password) {
            setMessage('Enter email and password.', true);
            return;
        }
        setMessage('Signing in...');
        try {
            const data = await apiJson('/api/auth/signin', {
                method: 'POST',
                body: JSON.stringify({ email, password }),
            });
            persistSession({
                access_token: data.access_token,
                refresh_token: data.refresh_token,
                user: data.user,
            });
            authPassword().value = '';
            setMessage('');
            await enterApp();
        } catch (e) {
            setMessage(e.message, true);
        }
    }

    async function signOut() {
        try {
            if (session?.access_token) {
                await apiJson('/api/auth/signout', { method: 'POST' });
            }
        } catch (e) {
            console.warn('Sign out API failed:', e.message);
        }
        persistSession(null);
        setMessage('Signed out. Sign in to continue.');
        showLogin();
        if (typeof onSignedOut === 'function') {
            onSignedOut();
        }
    }

    function bindUi() {
        document.getElementById('signInBtn')?.addEventListener('click', signIn);
        document.getElementById('signUpBtn')?.addEventListener('click', signUp);
        document.getElementById('signOutBtn')?.addEventListener('click', signOut);
        authPassword()?.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') {
                e.preventDefault();
                signIn();
            }
        });
    }

    async function bootstrap(callbacks = {}) {
        onAuthenticated = callbacks.onAuthenticated || null;
        onSignedOut = callbacks.onSignedOut || null;
        bindUi();
        restoreSession();

        if (isLoggedIn()) {
            const ok = await refreshMe();
            if (ok) {
                await enterApp();
                return;
            }
        }

        showLogin();
        setMessage('');
    }

    return {
        API_BASE,
        apiJson,
        authHeaders,
        getSession,
        isLoggedIn,
        bootstrap,
        signOut,
    };
})();
