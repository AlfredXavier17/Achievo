function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let cookie of cookies) {
            cookie = cookie.trim();
            if (cookie.startsWith(name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

const goalId = JSON.parse(document.getElementById('goal-data').textContent);
const titleInput = document.getElementById('goal-title');
const descriptionTextarea = document.getElementById('goal-description');
const autosaveMsg = document.getElementById('autosave-msg');

let timeoutId;

function autosaveGoal() {
    clearTimeout(timeoutId);
    timeoutId = setTimeout(() => {
        if (autosaveMsg) autosaveMsg.style.display = 'block';

        fetch(`/goals/${goalId}/autosave/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCookie('csrftoken') // ✅ CSRF token added
            },
            body: JSON.stringify({
                title: titleInput.value,
                description: descriptionTextarea.value
            })
        })
        .then(response => {
            if (!response.ok) throw new Error(`HTTP error! Status: ${response.status}`);
            return response.json();
        })
        .then(data => {
            if (autosaveMsg) {
                autosaveMsg.textContent = data.status === 'saved' ? 'Saved!' : 'Error saving.';
                setTimeout(() => autosaveMsg.style.display = 'none', 2000);
            }
        })
        .catch(error => {
            console.error('Autosave failed:', error);
            if (autosaveMsg) {
                autosaveMsg.textContent = 'Error saving.';
                setTimeout(() => autosaveMsg.style.display = 'none', 2000);
            }
        });
    }, 1000);
}

titleInput.addEventListener('input', autosaveGoal);
descriptionTextarea.addEventListener('input', autosaveGoal);

window.addEventListener('beforeunload', () => {
    const data = JSON.stringify({
        title: titleInput.value,
        description: descriptionTextarea.value
    });

    navigator.sendBeacon(`/goals/${goalId}/autosave/`, new Blob([data], { type: 'application/json' }));
});
