/** @odoo-module **/

import { Component, useState, onMounted } from "@odoo/owl";
import { registry } from "@web/core/registry";
import { NecesidadesClienteModal } from "./modals/necesidades_modal";

export class DtmNecesidadesClienteComponent extends Component {
    static components = { NecesidadesClienteModal };
    setup() {
        this.state = useState({
            necesidades: [],
            showModalNecesidades: false,
        });
        onMounted(() => {
            this.loadNecesidades();
        });
    }

    openModalNecesidades(ev) {
        console.log(ev);
        this.state.showModalNecesidades = true;
    }

    closeModalNecesidades = () => {
        this.state.showModalNecesidades = false;
    }
    // Despliega la información de la necesidad
    toggle(ev) {
        const item = ev.target.closest(".need-item");
        const open = item.children[1];
        const chev = item.children[0].children[1].children[1]

        open.classList.toggle("visible")
        chev.classList.toggle("open");
        item.classList.toggle("expanded");

    }
    async loadNecesidades() {
        const data = await fetch("/dtm_cotizaciones/get_necesidades");
        const necesidades = await data.json();
        console.log(necesidades);
        this.state.necesidades = necesidades;
    }
}

Component.template = "dtm_cotizaciones.dtm_necesidades_cliente_component";
registry.category("actions").add("dtm_cotizaciones.dtm_necesidades_cliente_component", DtmNecesidadesClienteComponent);
