const API = window.NEURO_API;
let CURRENT_LEAD_ID = null;

// Helpers
const $ = (sel) => document.querySelector(sel);
const el = (tag, cls, txt) => {
    const x = document.createElement(tag);
    if (cls) x.className = cls;
    if (txt !== undefined && txt !== null) x.textContent = txt;
    return x;
};

async function apiFetch(path, options) {
    const res = await fetch(`${API}${path}`, options);
    if (!res.ok) {
        let detail = res.statusText;
        try {
            const body = await res.json();
            detail = body.detail || JSON.stringify(body);
        } catch (_) { /* ignore */ }
        throw new Error(`${res.status}: ${detail}`);
    }
    return res.json();
}

// QUIZ SUBMIT
$("#quizForm").addEventListener("submit", async (e) => {
    e.preventDefault();
    const fd = new FormData(e.target);
    const payload = {
        nombre: fd.get("nombre"),
        email: fd.get("email") || null,
        whatsapp: fd.get("whatsapp") || null,
        fuente: "web",
        respuestas: [
            { pregunta: "Que necesitas hoy", respuesta: fd.get("q1") },
            { pregunta: "Urgencia", respuesta: fd.get("q2") },
            { pregunta: "Presupuesto", respuesta: fd.get("q3") },
            { pregunta: "Detalle", respuesta: fd.get("q4") },
        ],
    };

    const r = $("#quizResult");
    r.classList.remove("hidden");
    r.textContent = "Enviando…";

    try {
        const data = await apiFetch("/api/quiz/submit", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(payload),
        });

        r.innerHTML = `<strong>¡Listo ${payload.nombre}!</strong> Puntaje: <b>${data.puntaje}</b> — Estado: <b>${data.estado}</b>.`;
        CURRENT_LEAD_ID = data.lead_id;

        $("#chat").classList.remove("hidden");
        $("#chatBox").innerHTML = "";
        pushMsg("out", "¡Hola! Soy tu asistente 24/7. Pregúntame por horarios, garantía, servicio a domicilio o agenda una cita.");
        loadLeads();
    } catch (err) {
        r.textContent = `No se pudo enviar el quiz (${err.message}).`;
    }
});

// CHAT
function pushMsg(dir, text) {
    const box = $("#chatBox");
    box.appendChild(el("div", `msg ${dir}`, text));
    box.scrollTop = box.scrollHeight;
}

$("#chatForm").addEventListener("submit", async (e) => {
    e.preventDefault();
    const txt = $("#chatInput").value.trim();
    if (!txt || !CURRENT_LEAD_ID) return;
    $("#chatInput").value = "";
    pushMsg("in", txt);

    try {
        const data = await apiFetch("/api/chat", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ lead_id: CURRENT_LEAD_ID, mensaje: txt }),
        });
        pushMsg("out", data.reply);
    } catch (err) {
        pushMsg("out", `Error: ${err.message}`);
    }
});

// LEADS
async function loadLeads() {
    const tbody = $("#leadsTable tbody");
    try {
        const list = await apiFetch("/api/leads");
        tbody.innerHTML = "";
        list.forEach((l) => {
            const tr = el("tr");
            tr.appendChild(el("td", "", l.id));
            tr.appendChild(el("td", "", l.nombre));
            tr.appendChild(el("td", "", l.puntaje));
            tr.appendChild(el("td", "", l.estado));
            tr.appendChild(el("td", "", l.creado ? new Date(l.creado).toLocaleString() : ""));
            tbody.appendChild(tr);
        });
    } catch (err) {
        tbody.innerHTML = `<tr><td colspan="5">No se pudieron cargar los leads (${err.message}).</td></tr>`;
    }
}
$("#refreshLeads").addEventListener("click", loadLeads);
loadLeads();
