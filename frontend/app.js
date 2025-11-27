// API base URL
const API_BASE = 'http://localhost:8000';

// State management
let currentProductId = null;
let conversationHistory = [];

// DOM elements
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

// Initialize
async function init() {
    await loadProducts();
    setupEventListeners();
}

// Setup event listeners
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
}

// Load product list
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
            item.innerHTML = `
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

// Select product
async function selectProduct(productId) {
    try {
        const response = await fetch(`${API_BASE}/api/products/${productId}`);
        const product = await response.json();
        
        currentProductId = productId;
        conversationHistory = [];
        
        // Update UI
        productName.textContent = product.name;
        productInfo.textContent = `${product.reviews.length} reviews`;
        
        // Show selection in product list
        document.querySelectorAll('.product-item').forEach(item => {
            item.classList.remove('active');
        });
        event.currentTarget.classList.add('active');
        
        // Initialize chat
        chatContainer.innerHTML = `
            <div class="message assistant">
                <div class="message-content">
                    Hello! Ask me anything about ${product.name}. 
                    I'll answer based on ${product.reviews.length} actual user reviews. 😊
                </div>
            </div>
        `;
        
        // Enable input
        messageInput.disabled = false;
        sendBtn.disabled = false;
        messageInput.focus();
        
    } catch (error) {
        console.error('Failed to select product:', error);
        showError('Unable to load product information.');
    }
}

// Send message
async function sendMessage() {
    const message = messageInput.value.trim();
    if (!message || !currentProductId) return;
    
    // Display user message
    addMessage(message, 'user');
    messageInput.value = '';
    
    // Add to conversation history
    conversationHistory.push({
        role: 'user',
        content: message
    });
    
    // Show typing indicator
    const typingId = showTypingIndicator();
    
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
        
        // Remove typing indicator
        removeTypingIndicator(typingId);
        
        // Display AI response
        addMessage(data.response, 'assistant');
        
        // Add to conversation history
        conversationHistory.push({
            role: 'assistant',
            content: data.response
        });
        
    } catch (error) {
        removeTypingIndicator(typingId);
        console.error('Failed to send message:', error);
        addMessage('Sorry, unable to generate a response. Please try again.', 'assistant');
    }
}

// Add message
function addMessage(content, role) {
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${role}`;
    messageDiv.innerHTML = `
        <div class="message-content">${content}</div>
    `;
    chatContainer.appendChild(messageDiv);
    chatContainer.scrollTop = chatContainer.scrollHeight;
}

// Typing indicator
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

// Upload product
async function uploadProduct() {
    const productId = document.getElementById('productId').value.trim();
    const name = document.getElementById('productNameInput').value.trim();
    const description = document.getElementById('productDesc').value.trim();
    const reviewsText = document.getElementById('reviewsInput').value.trim();
    
    if (!productId || !name || !description) {
        alert('Please fill in all fields.');
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
                description: description,
                reviews: reviews
            })
        });
        
        const data = await response.json();
        
        if (data.status === 'success') {
            alert('Product uploaded successfully!');
            uploadModal.style.display = 'none';
            
            // Reset form
            document.getElementById('productId').value = '';
            document.getElementById('productNameInput').value = '';
            document.getElementById('productDesc').value = '';
            document.getElementById('reviewsInput').value = '';
            
            // Reload product list
            await loadProducts();
        } else {
            alert('Upload failed: ' + (data.detail || 'Unknown error'));
        }
        
    } catch (error) {
        console.error('Upload failed:', error);
        alert('Error during upload: ' + error.message);
    }
}

// Show error
function showError(message) {
    addMessage(message, 'assistant');
}

// Start app
init();

