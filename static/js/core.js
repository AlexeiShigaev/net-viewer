let devices
let macs_ip
let tree

function getNextLevelInTree(tree, devices, level) {
    let elem = Object.keys(tree)[0];

    let root_div = document.createElement('div');
    if (level === 1) {
        root_div.id = "wrapper";
    } else {
        root_div.classList.add("entry", "sole");
    }

    root_div.insertAdjacentHTML("beforeend",
        `<span class="label" id="` + devices[elem].host +
        `" data-bs-toggle="offcanvas" data-bs-target="#device_info">` +
        devices[elem].host + `<br>` + devices[elem].info + `</span>`
    );


    let level_div = document.createElement('div');
    level_div.classList.add("branch", "lv" + level);

    for (let port in devices[elem].ports) {
        let macs = Object.keys(devices[elem].ports[port].macs)
        if (macs.length) {
            let next_level_entry = document.createElement('div');
            next_level_entry.classList.add("entry");

            next_level_entry.insertAdjacentHTML("beforeend",
                `<span class="label">` +
                devices[elem].ports[port].name +
                ` (macs: ` + (macs.length) + ` )</span>`
            );

            if ((port in tree[elem].ports) && ('uplink' in tree[elem].ports[port])) {
                let uplink = tree[elem].ports[port]["uplink"];

                let level_div_new = document.createElement('div');
                const num_level = 1 + level;
                level_div_new.classList.add("branch", "lv" + num_level);

                level_div_new.append(
                    getNextLevelInTree(uplink, devices, level + 2)
                )

                next_level_entry.append(level_div_new);
            }
            let entry = next_level_entry.getElementsByClassName("entry");
            if (entry.length === 2) {
                entry[1].classList.add("sole")
            }
            level_div.append(next_level_entry);
        }
    }

    root_div.append(level_div)

    return root_div
}


document.getElementById("menu_refresh").addEventListener("click", loadPlace)

async function loadPlace() {
    try {
        let fetchResponse = await fetch("/core/get_place");
        if (!fetchResponse.ok)
            throw fetchResponse.status;
        else {
            let response = await fetchResponse.json();
            if (response.error) throw fetchResponse.status;
            devices = response.devices
            macs_ip = response.macs
            tree = response.tree

            let root_tree = getNextLevelInTree(tree, devices, 1)
            root_tree.addEventListener("click", show_device_info)

            document.getElementById("place").append(root_tree);
            // document.getElementById(devices[data[0]].host).addEventListener("click", show_device_info);
            console.log("finished ok");
        }
    } catch (e) {
        console.error("fetch crashes");
        document.getElementById("place").innerText = "что-то пошло не так: response " + e;
    }
}


function show_device_info(e) {
    let dev = e.target.id
    if (!(dev in devices)) return

    document.getElementById("offcanvas_device_info").innerHTML =
        `<p class="text-break fw-bold fs-2">Детализация по устройству ` + dev + `</p>`;

    document.getElementById("collapseInfoText").innerHTML = devices[dev].info;

    // console.log(devices[dev].internal_ip)

    let internal_ip = document.getElementById("collapseInternalIPText")
    internal_ip.innerHTML = `<h4 class="mt-4">Внутренние IP-адреса устройства.</h4>`
    let ips = devices[dev].internal_ip

    internal_ip.insertAdjacentHTML("beforeend", `
        <ul class="list-group list-group-horizontal-xl">
            <li class="list-group-item w-50">ip-address</li>
            <li class="list-group-item w-25">mask</li>
            <li class="list-group-item w-25">interface/vlan</li>
        </ul>
    `)

    for (let elem in ips) {
        // Может возникнуть ситуация, когда такого интерфейса нет в списке портов
        let iface = "?"
        try {
            iface = devices[dev].ports[ips[elem].ipAdEntIfIndex].name
        } catch {
        }

        internal_ip.insertAdjacentHTML("beforeend",
            `<ul class="list-group list-group-horizontal-xl">
                <li class="list-group-item w-50">` + ips[elem].ipAdEntAddr + `</li>
                <li class="list-group-item w-25">` + ips[elem].ipAdEntNetMask + `</li>
                <li class="list-group-item w-25">` + iface + `</li>
            </ul>`
        )
    }

    let ports_text = document.getElementById("collapsePortsText")
    ports_text.innerHTML = "<h3 class=\"mt-4\">Детализация по портам. MAC-адреса, IP-адреса, VLANs.</h3>"

    for (let elem in devices[dev].ports) {
        let port = devices[dev].ports[elem]

        if (Object.keys(port.macs).length > 0) {

            ports_text.insertAdjacentHTML("beforeend",
                `<h4 class="mt-4">` + port.name + `</h4>`
            )

            ports_text.insertAdjacentHTML("beforeend",
                `<ul class="list-group list-group-horizontal-xl">
                <li class="list-group-item w-50">mac</li>
                <li class="list-group-item w-25">ip-address</li>
                <li class="list-group-item w-25">vlan</li>
            </ul>`
            )

            for (let el in port.macs) {
                ports_text.insertAdjacentHTML(`beforeend`,
                    `<ul class="list-group list-group-horizontal-xl">
                    <li class="list-group-item w-50">` + el + `</li>
                    <li class="list-group-item w-25">` + macs_ip[el].join("<br>") + `</li>
                    <li class="list-group-item w-25">` + port.macs[el] + `</li>
                </ul>`
                )
            }
        }
    }
    console.log("show_device_info finished")
}

