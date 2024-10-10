////////////////////////////////////////////////////////////////////
// разлогиниться по пункту логаут
////////////////////////////////////////////////////////////////////
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
        return false
    }
    if (pass1.value !== pass2.value) {
        feedback.innerHTML = "подтверждение не совпадает с паролем";
        pass2.classList.add("is-invalid")
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
        if (!fetchResponse.ok) throw fetchResponse;
        else {
            alert("Пароль изменен.\nВы будете перенаправлены на страницу авторизации.")
            window.location.replace("/web");
        }

    } catch (e) {
        alert("Пароль изменить не удалось.")
        console.error("fetch crashes" + e);
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
// Первый запрос - к абстрактному эндпоинту. Дает сырые данные от устройства. Как есть.
// Второй запрос - к специальноу эндпоинту, он выдает обработанные данные.
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
        if (!fetchResponse.ok) throw fetchResponse.status;
        else {
            let response = await fetchResponse.json();
            let text = "";
            if (response.error) throw fetchResponse.status;
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
        if (!fetchResponse.ok) throw fetchResponse.status;
        else {
            let response = await fetchResponse.json();
            if (response.error) throw fetchResponse.status;

            let text = "";
            response.results_list.forEach(elem => {
                console.log(JSON.stringify(elem))
                text = text + JSON.stringify(elem) + "\n";
            })
            document.getElementById(tab + "-result2").value = text;
        }

    } catch (e) {
        console.error("fetch crashes: " + e);
        document.getElementById(tab + "-result2").innerText = "что-то пошло не так: response " + e;
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
        document.getElementById('isOK').checked = false

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
document.getElementById('isOK').addEventListener('click', function () {
    if (this.checked)
        document.getElementById("addButton").removeAttribute("disabled");
    else
        document.getElementById("addButton").setAttribute("disabled", '')

});

////////////////////////////////////////////////////////////////////
// Обращение к /core/add_device для добавления устройства
////////////////////////////////////////////////////////////////////
document.getElementById("addButton").addEventListener("click", sendNewDeviceData)

async function sendNewDeviceData() {
    try {
        let fetchResponse = await fetch("/core/add_device", {
                method: 'POST',
                headers: {'Content-type': 'application/json',},
                body: document.getElementById("new_device").value
            }
        );
        if (!fetchResponse.ok)
            throw fetchResponse.status;
        else
            document.getElementById("new_device").value = "Устройство добавлено.";
    } catch (e) {
        console.error("fetch crashes: " + e);
        document.getElementById("new_device").value = "что-то пошло не так: response " + e;
    }
    document.getElementById("addButton").setAttribute("disabled", '');
    document.getElementById('isOK').checked = false
}


////////////////////////////////////////////////////////////////////
// Поисковая строка. Делаем запрос,выдаем результат.
////////////////////////////////////////////////////////////////////
document.getElementById("searchButton").addEventListener("click", sendSearch)

async function sendSearch() {
    let query_str = document.getElementById("searchInput").value
    try {
        let fetchResponse = await fetch("/core/search/",
            {
                method: 'POST',
                headers: {'Content-type': 'application/json',},
                body: JSON.stringify({"query": query_str})
            }
        );
        document.getElementById("offcanvas_info_title").innerText = "Запрос: " + query_str
        if (!fetchResponse.ok)
            throw fetchResponse.status;
        else {
            let info = document.getElementById("offcanvas_info_body")
            let info_json = await fetchResponse.json()

            info.innerHTML = `
                <ul class="list-group list-group-horizontal-xl">
                    <li class="list-group-item w-50">ip-address</li>
                    <li class="list-group-item w-50">mac-address</li>
                </ul>
            `
            info.insertAdjacentHTML("beforeend",
                `<ul class="list-group list-group-horizontal-xl">
                    <li class="list-group-item w-50">` + Object.keys(info_json)[0] + `</li>
                    <li class="list-group-item w-50">` + info_json[Object.keys(info_json)[0]].mac + `</li>
                </ul>`
            )

            let devices = info_json[Object.keys(info_json)[0]].devices
            info.insertAdjacentHTML("beforeend", `<h4 class="mt-4">Какие устройства его знают:</h4>`)

            info.insertAdjacentHTML("beforeend", `
                <ul class="list-group list-group-horizontal-xl">
                    <li class="list-group-item w-25">Устройство</li>
                    <li class="list-group-item w-50">имя порта</li>
                    <li class="list-group-item w-25">кол-во маков на порту</li>
                </ul>
            `)
            for (let dev in devices) {
                info.insertAdjacentHTML("beforeend", `
                    <ul class="list-group list-group-horizontal-xl">
                        <li class="list-group-item w-25">` + dev + `</li>
                        <li class="list-group-item w-50">` + devices[dev].port_name + `</li>
                        <li class="list-group-item w-25">` + devices[dev].port_macs_counter + `</li>
                    </ul>
                `)
            }
        }
    } catch (e) {
        console.error("fetch crashes: " + e);
        document.getElementById("place").innerText = "что-то пошло не так: response " + e;
    }
}

document.getElementById("searchInput").addEventListener("keyup", ({key}) => {
    if (key === "Enter") {
        document.getElementById("searchButton").click()
    }
})

