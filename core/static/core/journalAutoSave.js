const journalId = JSON.parse(document.getElementById('journal-data').textContent);
const titleInput = document.getElementById('journal-title');
const contentTextarea = document.getElementById('journal-content');
const autosaveMsg = document.getElementById('autosave-msg');

let timeoutId;

function autosave() {
    clearTimeout(timeoutId);
    timeoutId = setTimeout(() => {
        autosaveMsg.style.display = 'inline';
        fetch(`/journals/${journalId}/autosave/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCookie('csrftoken')
            },
            body: JSON.stringify({
                title: titleInput.value,
                content: contentTextarea.value
            })
        })
        .then(response => response.json())
        .then(data => {
            autosaveMsg.innerText = 'Saved ✅';
            setTimeout(() => autosaveMsg.style.display = 'none', 1500);
        })
        .catch(error => {
            console.error('Error saving:', error);
            autosaveMsg.innerText = 'Error saving ❌';
        });
    }, 1000);
}

titleInput.addEventListener('input', autosave);
contentTextarea.addEventListener('input', autosave);

window.addEventListener('beforeunload', function () {
    const data = JSON.stringify({
        title: titleInput.value,
        content: contentTextarea.value
    });

    navigator.sendBeacon(`/journals/${journalId}/autosave/`, new Blob([data], { type: 'application/json' }));
});

function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}
