const goalId = JSON.parse(document.getElementById('goal-data').textContent);
const titleInput = document.getElementById('goal-title');
const descriptionTextarea = document.getElementById('goal-description');

let timeoutId;

function autosaveGoal() {
    clearTimeout(timeoutId);
    timeoutId = setTimeout(() => {
        fetch(`/goals/${goalId}/autosave/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCookie('csrftoken')
            },
            body: JSON.stringify({
                title: titleInput.value,
                description: descriptionTextarea.value
            })
        }).catch(error => {
            console.error('Autosave failed:', error);
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
