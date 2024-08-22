document.getElementById('menu_logout').addEventListener('click', function() {
    fetch("/auth/logout")
        .then(response => {
            window.location.href = "/web";
        })
});


document.getElementById('passwd2').addEventListener('keyup', validatePasswords);

function validatePasswords() {
    let pass1 = document.getElementById("passwd1");
    let pass2 = document.getElementById("passwd2");
    let feedback = document.getElementById("passwordFeedback")

    if (pass1.value.length < 4) {
        feedback.innerHTML = "пароль должен быть не менее трех символов";
        pass2.classList.add("is-invalid")
        console.log("pass < 4")
        return false
    }
    if (pass1.value !== pass2.value){
        feedback.innerHTML = "подтверждение не совпадает с паролем";
        pass2.classList.add("is-invalid")
        console.log("not equals")
        return false
    }
    console.log("all fine")
    feedback.innerHTML = "";
    document.getElementById('changePasswordButton').removeAttribute("disabled");
    pass2.classList.remove("is-invalid")
    return true
}


document.getElementById('changePasswordButton').addEventListener('click', ChangePasswordButton);
async function ChangePasswordButton() {
    try {
        const fetchResponse = await fetch("/auth/change_passwd", {
                method: 'POST',
                headers: {
                    'Accept': 'application/json',
                    'Content-type': 'application/json',
                },
                body: JSON.stringify({
                    "login": "self",
                    "password": document.getElementById("passwd1").value
                })
            }
        );
        if (!fetchResponse.ok){
            throw fetchResponse;
        }
        else {
            alert("Пароль изменен.\nВы будете перенаправлены на страницу авторизации.")
            window.location.replace("/web");
        }

    } catch(e) {
        alert("Пароль изменить не удалось.")
        console.error("fetch crashes");
    }
}

document.getElementById('changePassword').addEventListener('shown.bs.modal', function(){
    document.getElementById("passwd1").focus();
});

