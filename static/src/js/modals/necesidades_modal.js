/** @odoo-module **/

import { Component, useState } from "@odoo/owl";

export class NecesidadesClienteModal extends Component {
    static props = ["close"]

    setup() {
        this.state = useState({
            clientes: [],
            mostrarDropdown: false,
            requisitores: [],
            requisitoresSeleccionados: [],
        });
    }

    selectCliente(cliente) {
        const input = document.getElementById("cliente");
        input.value = cliente.name;
        this.state.mostrarDropdown = false;
        this.state.clientes = [];
    }

    async onInputCliente(event) {
        this.state.mostrarDropdown = event.target.value ? true : false;
        if (event.target.value) {
            const response = await fetch("/restpartner_client", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                },
                body: JSON.stringify({
                    name: event.target.value,
                }),
            });
            const data = await response.json();
            this.state.clientes = data.result;
        }

    }

}

NecesidadesClienteModal.template = "dtm_cotizaciones.necesidades_modal";