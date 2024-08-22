document.getElementById('submitButton').addEventListener('click', LogonButton);

async function LogonButton() {
    try {
        let fetchResponse = await fetch("/auth/logon", {
                method: 'POST',
                headers: {
                    'Accept': 'application/json, text/plain, */*',
                    'Content-type': 'application/json',
                },
                body: JSON.stringify({
                    "login": document.getElementById("username").value,
                    "password": document.getElementById("password").value
                })
            }
        );
        if (!fetchResponse.ok){
            throw fetchResponse;
        }
        else {
            window.location.replace("/web/client");
        }
    } catch {
        console.error("fetch crashes");
    }
}
