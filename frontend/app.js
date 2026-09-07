// Wires auth, products, chat, and saved-products after login.

let appStarted = false;

async function startApp() {
    if (!appStarted) {
        Products.bind();
        Chat.bind();
        Saved.bind();
        appStarted = true;
    }
    await Products.load();
    await Saved.loadList();
}

function handleSignedOut() {
    Chat.reset();
    Products.resetList();
    Saved.reset();
}

Auth.bootstrap({
    onAuthenticated: startApp,
    onSignedOut: handleSignedOut,
});
