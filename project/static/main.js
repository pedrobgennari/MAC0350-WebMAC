async function signup() {
    const data = {
        name: document.getElementById('name').value,
        password: document.getElementById('password').value
    };

    if (data.name === ''){
        alert("Escolha um nome de usuário!");
        return;
    }

    const answer = await fetch('/newuser', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(data)
    });

    if (answer.ok) {
        const result = await answer.json();
        alert(result.message);
    }
    else {
        alert("Erro ao enviar!");
    }
}

async function login() {
    const data = {
        name: document.getElementById('name').value,
        password: document.getElementById('password').value
    };

    const answer = await fetch('/login', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(data)
    });

    if (answer.ok) {
        const result = await answer.json();
        alert(result.message);
    }
    else {
        alert("Erro ao enviar!");
    }
}
