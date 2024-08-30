// разлогиниться по пункту логаут
document.getElementById('menu_logout').addEventListener('click', function () {
    fetch("/auth/logout")
        .then(response => {
            window.location.href = "/web";
        })
});


////////////////////////////////////////////////////////////////////
// Для модального окна смены пароля текущего пользователя.
// валидатор подтверждения
////////////////////////////////////////////////////////////////////
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
    if (pass1.value !== pass2.value) {
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

////////////////////////////////////////////////////////////////////
// Для модального окна смены пароля текущего пользователя.
// Запрос на смену пароля.
////////////////////////////////////////////////////////////////////
document.getElementById('changePasswordButton').addEventListener('click', ChangePasswordButton);

async function ChangePasswordButton() {
    try {
        const fetchResponse = await fetch("/auth/change_passwd", {
                method: 'POST',
                headers: {
                    // 'Accept': 'application/json',
                    'Content-type': 'application/json',
                },
                body: JSON.stringify({
                    "login": "self",
                    "password": document.getElementById("passwd1").value
                })
            }
        );
        if (!fetchResponse.ok) {
            throw fetchResponse;
        } else {
            alert("Пароль изменен.\nВы будете перенаправлены на страницу авторизации.")
            window.location.replace("/web");
        }

    } catch (e) {
        alert("Пароль изменить не удалось.")
        console.error("fetch crashes");
    }
}

// в модальном окне не работает autofocus
document.getElementById('changePassword').addEventListener('shown.bs.modal', function () {
    document.getElementById("passwd1").focus();
    let btn = document.getElementById('changePasswordButton');
    btn.setAttribute("disabled", '');
})

////////////////////////////////////////////////////////////////////
// УРЛы для тестовых запросов из модального окна добавления нового устройства.
////////////////////////////////////////////////////////////////////
const urls = {
    "tab-connect": "/snmp/query/info",
    "tab-info": "/snmp/query/info",
    "tab-ports": "/snmp/query/ports",
    "tab-macs": "/snmp/query/macs",
    "tab-ip": "/snmp/query/info_ip",
    "tab-arp": "/snmp/query/arp"
}

////////////////////////////////////////////////////////////////////
// Тестирование запроса к устройству в модальном окне добавления нового устройства
// первый запрос - к абстрактному эндпоинту. Дает сырые данные от устройства. как есть.
// второй запрос - к специальноу эндпоинту, он выдает обработанные данные.
////////////////////////////////////////////////////////////////////
async function runTest(tab) {
    let versionSNMP = 0
    if (document.getElementById("tab-connect-version2").checked) versionSNMP = 1

    const data = JSON.stringify(
        {
            "community": document.getElementById("community").value,
            "host": document.getElementById("ip-addr").value,
            "oid_start": document.getElementById(tab + "-start-oid").value,
            "oid_stop": document.getElementById(tab + "-stop-oid").value,
            "port": document.getElementById("port").value,
            "snmp_ver": versionSNMP
        }
    );

    document.getElementById(tab + "-result1").value = "запрос";
    document.getElementById(tab + "-result2").value = "запрос";

    try {
        let fetchResponse = await fetch("/snmp", {
                method: 'POST',
                headers: {'Content-type': 'application/json',},
                body: data
            }
        );
        if (!fetchResponse.ok) {
            document.getElementById(tab + "-result1").value = "Не удалось получить данные: response " + e.status;
            throw fetchResponse;
        } else {
            let response = await fetchResponse.json();
            let text = "";
            if (response.error) {
                document.getElementById(tab + "-result1").value = "Устройство не настроено отвечать на запросы";
                throw fetchResponse;
            }
            // console.log(response)
            response.results_list.forEach(elem => {
                text = text + elem["oid"] + "=" + elem["value"] + "\n";
            })
            document.getElementById(tab + "-result1").value = text;
        }

        // вынимаем полезные данные штатным эндпоинтом
        fetchResponse = await fetch(urls[tab], {
                method: 'POST',
                headers: {'Content-type': 'application/json',},
                body: data
            }
        );
        if (!fetchResponse.ok) {
            document.getElementById(tab + "-result2").value = "Не удалось получить данные: response " + e.status;
            throw fetchResponse;
        } else {
            let response = await fetchResponse.json();
            if (response.error) {
                document.getElementById(tab + "-result2").value = "Ошибка парсинга данных";
                throw fetchResponse;
            }
            let text = "";
            console.log(response)
            response.results_list.forEach(elem => {
                console.log(JSON.stringify(elem))
                text = text + JSON.stringify(elem) + "\n";
            })
            document.getElementById(tab + "-result2").value = text;
        }

    } catch (e) {
        console.error("fetch crashes");
        document.getElementById(tab + "-result2").value = "что-то пошло не так: response " + e.status;
    }
}

////////////////////////////////////////////////////////////////////
// Модальное окно добавления нового устройства.
// В нем последняя закладка для подтверждения и отправки.
// При открытии это вкладки собираю данные с других закладок
////////////////////////////////////////////////////////////////////
document.getElementById('addSNMP').addEventListener('shown.bs.tab', function (e) {
    if (e.target.toString().endsWith("tab-confirm")) {
        document.getElementById("addButton").setAttribute("disabled", '');

        let versionSNMP = 0;
        if (document.getElementById("tab-connect-version2").checked) versionSNMP = 1

        document.getElementById("new_device").value = JSON.stringify({
            "host": document.getElementById("ip-addr").value,
            "port": document.getElementById("port").value,
            "community": document.getElementById("community").value,
            "snmp_ver": versionSNMP,
            "info_oid_start": document.getElementById("tab-info-start-oid").value,
            "info_oid_stop": document.getElementById("tab-info-stop-oid").value,
            "ports_oid_start": document.getElementById("tab-ports-start-oid").value,
            "ports_oid_stop": document.getElementById("tab-ports-stop-oid").value,
            "internal_ip_oid_start": document.getElementById("tab-ip-start-oid").value,
            "internal_ip_oid_stop": document.getElementById("tab-ip-stop-oid").value,
            "macs_oid_start": document.getElementById("tab-macs-start-oid").value,
            "macs_oid_stop": document.getElementById("tab-macs-stop-oid").value,
            "arp_oid_start": document.getElementById("tab-arp-start-oid").value,
            "arp_oid_stop": document.getElementById("tab-arp-stop-oid").value,
        })
    }
})

////////////////////////////////////////////////////////////////////
// Прежде чем отправить данные о новом устройстве надо поставить галочку
// для активации кнопки Добавить
////////////////////////////////////////////////////////////////////
document.getElementById('isOK').addEventListener('click', function(){
    if (this.checked)
        document.getElementById("addButton").removeAttribute("disabled");
    else
        document.getElementById("addButton").setAttribute("disabled", '')

});

////////////////////////////////////////////////////////////////////
// Обращение к /core/add_device для добавления устройства
////////////////////////////////////////////////////////////////////
document.getElementById("addButton").addEventListener("click", sendNewDeviceDada)
async function sendNewDeviceDada(){
    try{
        let fetchResponse = await fetch("/core/add_device", {
                method: 'POST',
                headers: {'Content-type': 'application/json',},
                body: document.getElementById("new_device").value
            }
        );
        if (!fetchResponse.ok) {
            document.getElementById("new_device").value = "Не удалось получить данные: response " + e.status;
            throw fetchResponse;
        } else {
            // let response = await fetchResponse.json();
            // if (response.error) {
            //     document.getElementById("new_device").value = "Ошибка парсинга данных";
            //     throw fetchResponse;
            // }
            document.getElementById("new_device").value = "Device added.";
        }

    } catch (e) {
        console.error("fetch crashes");
        document.getElementById("new_device").value = "что-то пошло не так: response " + e.status;
    }
}

