const API = window.NEURO_API;
let CURRENT_LEAD_ID = null;

// Helpers
const $ = (sel) => document.querySelector(sel);
const el = (tag, cls, txt) => {
    const x = document.createElement(tag);
    if (cls) x.className = cls;
    if (txt) x.textContent = txt;
    return x;
};

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
            { pregunta: "Qué necesitas hoy", respuesta: fd.get("q1") },
            { pregunta: "Urgencia", respuesta: fd.get("q2") },
            { pregunta: "Presupuesto", respuesta: fd.get("q3") },
            { pregunta: "Detalle", respuesta: fd.get("q4") },
        ],
    };

    const res = await fetch(`${API}/api/quiz/submit`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
    });
    const data = await res.json();

    const r = $("#quizResult");
    r.classList.remove("hidden");
    r.innerHTML = `<strong>¡Listo ${payload.nombre}!</strong> Puntaje: <b>${data.puntaje}</b> — Estado: <b>${data.estado}</b>.`;
    CURRENT_LEAD_ID = data.lead_id;

    // mostrar chat
    $("#chat").classList.remove("hidden");
    pushMsg("out", "¡Hola! Soy tu asistente 24/7. Pregúntame horarios, garantía, domicilio o agenda una cita.");
});

// CHAT
function pushMsg(dir, text) {
    const box = $("#chatBox");
    const m = el("div", `msg ${dir}`);
    m.textContent = text;
    box.appendChild(m);
    box.scrollTop = box.scrollHeight;
}

$("#chatForm").addEventListener("submit", async (e) => {
    e.preventDefault();
    const txt = $("#chatInput").value.trim();
    if (!txt || !CURRENT_LEAD_ID) return;
    $("#chatInput").value = "";
    pushMsg("in", txt);

    const res = await fetch(`${API}/api/chat`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ lead_id: CURRENT_LEAD_ID, mensaje: txt }),
    });
    const data = await res.json();
    pushMsg("out", data.reply);
});

// LEADS
async function loadLeads() {
    const res = await fetch(`${API}/api/leads`);
    const list = await res.json();
    const tbody = $("#leadsTable tbody");
    tbody.innerHTML = "";
    list.forEach((l) => {
        const tr = el("tr");
        tr.appendChild(el("td", "", l.id));
        tr.appendChild(el("td", "", l.nombre));
        tr.appendChild(el("td", "", l.puntaje));
        tr.appendChild(el("td", "", l.estado));
        tr.appendChild(el("td", "", "")); // CreatedAt lo omitimos del schema simplificado
        tbody.appendChild(tr);
    });
}
$("#refreshLeads").addEventListener("click", loadLeads);
loadLeads();
