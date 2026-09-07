// Chatbot + saved products (runs only after Auth bootstrap succeeds)

const API_BASE = Auth.API_BASE;

// State
let currentProductId = null;
let conversationHistory = [];
let appStarted = false;

// DOM
const productList = document.getElementById('productList');
const chatContainer = document.getElementById('chatContainer');
const messageInput = document.getElementById('messageInput');
const sendBtn = document.getElementById('sendBtn');
const uploadBtn = document.getElementById('uploadBtn');
const uploadModal = document.getElementById('uploadModal');
const closeModal = document.querySelector('.close');
const submitUpload = document.getElementById('submitUpload');
const productName = document.getElementById('productName');
const productInfo = document.getElementById('productInfo');
const savePanel = document.getElementById('savePanel');
const interestLevel = document.getElementById('interestLevel');
const personalNote = document.getElementById('personalNote');
const saveProductBtn = document.getElementById('saveProductBtn');
const removeSavedBtn = document.getElementById('removeSavedBtn');
const saveMessage = document.getElementById('saveMessage');
const savedList = document.getElementById('savedList');

function setSaveMessage(text, isError = false) {
    saveMessage.textContent = text || '';
    saveMessage.classList.toggle('error', Boolean(isError && text));
}

function updateSavePanelVisibility() {
    const show = Boolean(currentProductId);
    savePanel.classList.toggle('hidden', !show);
    if (show) saveProductBtn.disabled = false;
}

function resetChatWelcome() {
    currentProductId = null;
    conversationHistory = [];
    productName.textContent = 'Select a product';
    productInfo.textContent = '';
    savePanel.classList.add('hidden');
    interestLevel.value = 'interested';
    personalNote.value = '';
    removeSavedBtn.classList.add('hidden');
    saveProductBtn.textContent = 'Save to My List';
    setSaveMessage('');
    messageInput.disabled = true;
    sendBtn.disabled = true;
    chatContainer.innerHTML = `
        <div class="welcome-message">
            <h2>👋 Welcome!</h2>
            <p>Select a product and ask any questions.</p>
            <p>We'll answer based on actual user reviews.</p>
        </div>
    `;
    document.querySelectorAll('.product-item').forEach(item => item.classList.remove('active'));
}

async function startApp() {
    if (!appStarted) {
        setupEventListeners();
        appStarted = true;
    }
    await loadProducts();
    await loadSavedProducts();
}

function handleSignedOut() {
    resetChatWelcome();
    productList.innerHTML = '<p class="empty-message">Upload a product</p>';
    savedList.innerHTML = '<p class="empty-message">No saved products yet</p>';
}

async function loadSavedProducts() {
    if (!Auth.isLoggedIn()) return;
    try {
        const data = await Auth.apiJson('/api/saved-products');
        const items = data.items || [];
        savedList.innerHTML = '';
        if (items.length === 0) {
            const p = document.createElement('p');
            p.className = 'empty-message';
            p.textContent = 'No saved products yet';
            savedList.appendChild(p);
            return;
        }
        items.forEach(item => {
            const el = document.createElement('div');
            el.className = 'saved-item';
            el.dataset.productId = item.product_id;

            const title = document.createElement('h4');
            title.textContent = item.product_name || item.product_id;

            const meta = document.createElement('p');
            meta.textContent = formatInterest(item.interest_level);

            el.append(title, meta);
            if (item.personal_note) {
                const note = document.createElement('p');
                note.className = 'saved-note';
                note.textContent = item.personal_note;
                el.appendChild(note);
            }
            el.addEventListener('click', () => selectProduct(item.product_id));
            savedList.appendChild(el);
        });
    } catch (e) {
        savedList.innerHTML = '';
        const p = document.createElement('p');
        p.className = 'empty-message';
        p.textContent = `Unable to load saved list: ${e.message}`;
        savedList.appendChild(p);
    }
}

function formatInterest(level) {
    if (level === 'interested') return 'Interested';
    if (level === 'maybe') return 'Maybe';
    if (level === 'not_for_me') return 'Not for me';
    return level || '';
}

async function loadSavedForCurrentProduct() {
    if (!Auth.isLoggedIn() || !currentProductId) return;
    setSaveMessage('');
    try {
        const data = await Auth.apiJson(`/api/saved-products/${encodeURIComponent(currentProductId)}`);
        const item = data.item;
        if (item) {
            interestLevel.value = item.interest_level || 'interested';
            personalNote.value = item.personal_note || '';
            removeSavedBtn.classList.remove('hidden');
            saveProductBtn.textContent = 'Update Saved';
            setSaveMessage('Already in your list — edit and save to update.');
        } else {
            interestLevel.value = 'interested';
            personalNote.value = '';
            removeSavedBtn.classList.add('hidden');
            saveProductBtn.textContent = 'Save to My List';
        }
    } catch (e) {
        setSaveMessage(e.message, true);
    }
}

async function handleSaveProduct() {
    if (!Auth.isLoggedIn() || !currentProductId) return;
    setSaveMessage('Saving...');
    try {
        await Auth.apiJson('/api/saved-products', {
            method: 'POST',
            body: JSON.stringify({
                product_id: currentProductId,
                interest_level: interestLevel.value,
                personal_note: personalNote.value.trim(),
            }),
        });
        setSaveMessage('Saved to your list.');
        removeSavedBtn.classList.remove('hidden');
        saveProductBtn.textContent = 'Update Saved';
        await loadSavedProducts();
    } catch (e) {
        setSaveMessage(e.message, true);
    }
}

async function handleRemoveSaved() {
    if (!Auth.isLoggedIn() || !currentProductId) return;
    setSaveMessage('Removing...');
    try {
        await Auth.apiJson(`/api/saved-products/${encodeURIComponent(currentProductId)}`, {
            method: 'DELETE',
        });
        interestLevel.value = 'interested';
        personalNote.value = '';
        removeSavedBtn.classList.add('hidden');
        saveProductBtn.textContent = 'Save to My List';
        setSaveMessage('Removed from your list.');
        await loadSavedProducts();
    } catch (e) {
        setSaveMessage(e.message, true);
    }
}

function setupEventListeners() {
    sendBtn.addEventListener('click', sendMessage);
    messageInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            sendMessage();
        }
    });

    uploadBtn.addEventListener('click', () => {
        uploadModal.style.display = 'block';
    });

    closeModal.addEventListener('click', () => {
        uploadModal.style.display = 'none';
    });

    window.addEventListener('click', (e) => {
        if (e.target === uploadModal) {
            uploadModal.style.display = 'none';
        }
    });

    submitUpload.addEventListener('click', uploadProduct);
    saveProductBtn.addEventListener('click', handleSaveProduct);
    removeSavedBtn.addEventListener('click', handleRemoveSaved);
}

async function loadProducts() {
    try {
        const response = await fetch(`${API_BASE}/api/products`);
        const data = await response.json();
        
        if (data.products.length === 0) {
            productList.innerHTML = '<p class="empty-message">Upload a product</p>';
            return;
        }

        productList.innerHTML = '';
        data.products.forEach(product => {
            const item = document.createElement('div');
            item.className = 'product-item';
            item.dataset.productId = product.product_id;
            
            const imageHtml = product.image 
                ? `<img src="${product.image}" alt="${product.name}" style="width: 50px; height: 50px; object-fit: cover; border-radius: 5px; margin-bottom: 5px;">` 
                : '';
            
            item.innerHTML = `
                ${imageHtml}
                <h3>${product.name}</h3>
                <p>${product.reviews_count} reviews</p>
            `;
            item.addEventListener('click', () => selectProduct(product.product_id));
            productList.appendChild(item);
        });
    } catch (error) {
        console.error('Failed to load products:', error);
        showError('Unable to load product list.');
    }
}

async function selectProduct(productId) {
    try {
        const response = await fetch(`${API_BASE}/api/products/${productId}`);
        const product = await response.json();
        
        currentProductId = productId;
        conversationHistory = [];
        
        productName.textContent = product.name;
        productInfo.textContent = `${product.reviews.length} reviews`;
        
        document.querySelectorAll('.product-item').forEach(item => {
            item.classList.remove('active');
            if (item.dataset.productId === productId) {
                item.classList.add('active');
            }
        });
        
        chatContainer.innerHTML = `
            <div class="message assistant">
                <div class="message-content">
                    Hello! Ask me anything about ${product.name}. 
                    I'll answer based on ${product.reviews.length} actual user reviews. 😊
                </div>
            </div>
        `;
        
        setInputEnabled(true);
        updateSavePanelVisibility();
        await loadSavedForCurrentProduct();
        
    } catch (error) {
        console.error('Failed to select product:', error);
        showError('Unable to load product information.');
    }
}

async function sendMessage() {
    const message = messageInput.value.trim();
    if (!message || !currentProductId) return;
    
    addMessage(message, 'user');
    messageInput.value = '';
    
    conversationHistory.push({
        role: 'user',
        content: message
    });
    
    const typingId = showTypingIndicator();
    setInputEnabled(false);
    
    try {
        const response = await fetch(`${API_BASE}/api/chat`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                product_id: currentProductId,
                message: message,
                conversation_history: conversationHistory
            })
        });
        
        const data = await response.json();
        
        if (!response.ok) {
            throw new Error(data.detail || `Request failed (${response.status})`);
        }
        
        removeTypingIndicator(typingId);
        
        addMessage(data.response, 'assistant', {
            sources: data.sources,
            insufficientEvidence: data.insufficient_evidence
        });
        
        conversationHistory.push({
            role: 'assistant',
            content: data.response.replace(/\[\d+\]/g, '')
        });
        
    } catch (error) {
        removeTypingIndicator(typingId);
        console.error('Failed to send message:', error);
        addMessage(`Sorry, unable to generate a response. ${error.message}`, 'assistant', { isError: true });
    } finally {
        setInputEnabled(true);
    }
}

function setInputEnabled(enabled) {
    messageInput.disabled = !enabled;
    sendBtn.disabled = !enabled;
    sendBtn.textContent = enabled ? 'Send' : 'Sending...';
    if (enabled) messageInput.focus();
}

function addMessage(content, role, options = {}) {
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${role}`;
    
    const contentDiv = document.createElement('div');
    contentDiv.className = 'message-content';
    if (options.isError) contentDiv.classList.add('error');
    
    if (options.insufficientEvidence) {
        const notice = document.createElement('div');
        notice.className = 'evidence-notice';
        notice.textContent = '⚠️ Not enough evidence in the reviews';
        contentDiv.appendChild(notice);
    }
    
    contentDiv.appendChild(renderAnswerText(content));
    
    const sources = options.sources || [];
    if (sources.length > 0) {
        contentDiv.appendChild(renderSources(sources));
        linkCitations(contentDiv);
    }
    
    messageDiv.appendChild(contentDiv);
    chatContainer.appendChild(messageDiv);
    chatContainer.scrollTop = chatContainer.scrollHeight;
}

function renderAnswerText(content) {
    const wrapper = document.createElement('div');
    wrapper.className = 'answer-text';
    
    String(content).split(/(\[\d+\])/).forEach(part => {
        const match = part.match(/^\[(\d+)\]$/);
        if (match) {
            const marker = document.createElement('sup');
            marker.className = 'citation-marker';
            marker.dataset.marker = match[1];
            marker.textContent = part;
            marker.title = `Show review ${match[1]}`;
            wrapper.appendChild(marker);
        } else if (part) {
            wrapper.appendChild(document.createTextNode(part));
        }
    });
    
    return wrapper;
}

function renderSources(sources) {
    const details = document.createElement('details');
    details.className = 'sources';
    
    const summary = document.createElement('summary');
    summary.textContent = `Sources (${sources.length} review${sources.length === 1 ? '' : 's'})`;
    details.appendChild(summary);
    
    sources.forEach(source => {
        const card = document.createElement('div');
        card.className = 'source-card';
        card.dataset.marker = source.marker;
        
        const parts = [`[${source.marker}]`, source.review_id];
        if (source.rating !== null && source.rating !== undefined) parts.push(`★ ${source.rating}`);
        if (source.date) parts.push(source.date);
        
        const meta = document.createElement('div');
        meta.className = 'source-meta';
        meta.textContent = parts.join(' · ');
        
        const quote = document.createElement('p');
        quote.className = 'source-content';
        quote.textContent = source.content;
        
        card.append(meta, quote);
        details.appendChild(card);
    });
    
    return details;
}

function linkCitations(contentDiv) {
    const details = contentDiv.querySelector('.sources');
    
    contentDiv.querySelectorAll('.citation-marker').forEach(marker => {
        marker.addEventListener('click', () => {
            const card = details.querySelector(`.source-card[data-marker="${marker.dataset.marker}"]`);
            if (!card) return;
            
            details.open = true;
            details.querySelectorAll('.source-card').forEach(c => c.classList.remove('highlighted'));
            card.classList.add('highlighted');
            card.scrollIntoView({ block: 'nearest' });
        });
    });
}

function showTypingIndicator() {
    const id = 'typing-' + Date.now();
    const typingDiv = document.createElement('div');
    typingDiv.id = id;
    typingDiv.className = 'message assistant';
    typingDiv.innerHTML = `
        <div class="typing-indicator">
            <span></span>
            <span></span>
            <span></span>
        </div>
    `;
    chatContainer.appendChild(typingDiv);
    chatContainer.scrollTop = chatContainer.scrollHeight;
    return id;
}

function removeTypingIndicator(id) {
    const element = document.getElementById(id);
    if (element) element.remove();
}

async function uploadProduct() {
    const productId = document.getElementById('productId').value.trim();
    const name = document.getElementById('productNameInput').value.trim();
    const image = document.getElementById('productImage').value.trim();
    const description = document.getElementById('productDesc').value.trim();
    const reviewsText = document.getElementById('reviewsInput').value.trim();
    
    if (!productId || !name || !description) {
        alert('Please fill in all required fields.');
        return;
    }
    
    let reviews = [];
    if (reviewsText) {
        try {
            reviews = JSON.parse(reviewsText);
        } catch (error) {
            alert('Invalid JSON format for reviews.');
            return;
        }
    }
    
    try {
        const response = await fetch(`${API_BASE}/api/products/upload`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                product_id: productId,
                name: name,
                image: image || null,
                description: description,
                reviews: reviews
            })
        });
        
        const data = await response.json();
        
        if (data.status === 'success') {
            alert('Product uploaded successfully!');
            uploadModal.style.display = 'none';
            
            document.getElementById('productId').value = '';
            document.getElementById('productNameInput').value = '';
            document.getElementById('productImage').value = '';
            document.getElementById('productDesc').value = '';
            document.getElementById('reviewsInput').value = '';
            
            await loadProducts();
        } else {
            alert('Upload failed: ' + (data.detail || 'Unknown error'));
        }
        
    } catch (error) {
        console.error('Upload failed:', error);
        alert('Error during upload: ' + error.message);
    }
}

function showError(message) {
    addMessage(message, 'assistant', { isError: true });
}

// Gate: login first, then chatbot
Auth.bootstrap({
    onAuthenticated: startApp,
    onSignedOut: handleSignedOut,
});
