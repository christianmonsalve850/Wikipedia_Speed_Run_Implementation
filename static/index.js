/* ======================
   DOM REFERENCES
====================== */

/**
 * Short DOM lookup for frequently used elements.
 * @type {{form: HTMLFormElement, loader: HTMLElement, closeBtn: HTMLElement, results: HTMLElement}}
 */
const DOM = {
    form: document.getElementById("run-form"),
    loader: document.querySelector(".loading-overlay"),
    closeBtn: document.getElementById("closeLoading"),
    results: document.getElementById("results")
};

/* ======================
   UI STATE
====================== */

/**
 * Show the global loading modal and lock page scrolling.
 *
 * @return {void}
 */
function showLoader() {
    document.body.classList.add("modal-open");
    DOM.loader.style.display = "flex";
}

/**
 * Hide the global loading modal and restore page scrolling.
 *
 * @return {void}
 */
function hideLoader() {
    document.body.classList.remove("modal-open");
    DOM.loader.style.display = "none";
}

/**
 * Close any open error modal and restore page state.
 *
 * @return {void}
 */
function closeModal() {
    const modal = document.getElementById("errorModal");
    modal?.remove();
    document.body.classList.remove("modal-open");
}

/* ======================
   AUTOCOMPLETE
====================== */

/**
 * Attach autocomplete behavior to a text input and a suggestions list.
 *
 * - Sends debounced requests as the user types.
 * - Uses AbortController to cancel in-flight requests when a newer one starts.
 *
 * @param {string} inputId - id attribute of the text input element.
 * @param {string} listId - id attribute of the <ul> element used for suggestions.
 * @return {void}
 */
function attachAutocomplete(inputId, listId) {
    const input = document.getElementById(inputId);
    const list = document.getElementById(listId);
    let controller;

    input.addEventListener("input", async () => {
        const q = input.value.trim();
        list.innerHTML = "";
        if (q.length < 2) return;

        // Abort previous request (fast-typing optimization)
        controller?.abort();
        controller = new AbortController();

        try {
            // encodeURIComponent avoids issues with special characters
            const res = await fetch(`/autocomplete?q=${encodeURIComponent(q)}`, {
                signal: controller.signal
            });
            const data = await res.json();

            data.forEach(title => {
                const li = document.createElement("li");
                li.textContent = title;
                li.onclick = () => {
                    input.value = title;
                    list.innerHTML = "";
                };
                list.appendChild(li);
            });
        } catch (e) {
            // Ignore aborts; surface other unexpected errors for dev debugging.
            if (e.name !== "AbortError") console.error(e);
        }
    });

    // Clicking outside the input should clear suggestions.
    // Using contains avoids closing when interacting with the input itself.
    document.addEventListener("click", e => {
        if (!input.contains(e.target)) list.innerHTML = "";
    });
}

/* ======================
   SEARCH FLOW
====================== */

let abortController;

/**
 * Kick off the search run: show loader, POST form data, handle response.
 *
 * @return {Promise<void>}
 */
async function startRun() {
    abortController = new AbortController();
    showLoader();

    try {
        const res = await fetch("/run", {
            method: "POST",
            body: new FormData(DOM.form),
            signal: abortController.signal
        });

        const data = await res.json();
        hideLoader();

        data.status === "OK"
            ? renderResults(data)
            : showError(data.message);

    } catch (err) {
        hideLoader();
        if (err.name !== "AbortError") console.error(err);
    }
}

/**
 * Cancel the active run: abort client-side request and notify server to cancel.
 *
 * @return {void}
 */
function cancelRun() {
    abortController?.abort();
    // fire-and-forget: server will set its cancel flag
    fetch("/cancel", { method: "POST" });
}

/* ======================
   RENDERING
====================== */

/**
 * Render a successful search result into the results container.
 *
 * @param {{links: string[], elapsed_time: number}} data - Response payload.
 * @return {void}
 */
function renderResults(data) {
    DOM.results.innerHTML = `
        <div class="card">
            <h3>Path Found</h3>
            <ol class="path-list">
                ${data.links.map(l => `
                    <li>
                        <a href="https://en.wikipedia.org/wiki/${l.replaceAll(" ", "_")}"
                           target="_blank">
                           ${l}
                        </a>
                    </li>
                `).join("")}
            </ol>
        </div>
        <h4>Time: ${data.elapsed_time.toFixed(2)} seconds</h4>
    `;
}

/**
 * Display an error modal with a message.
 *
 * @param {string} msg - Error message to show.
 * @return {void}
 */
function showError(msg) {
    document.body.classList.add("modal-open");
    DOM.results.innerHTML = `
        <div class="modal-overlay" id="errorModal">
            <div class="modal">
                <h2>Search Error</h2>
                <p>${msg}</p>
                <button onclick="closeModal()">OK</button>
            </div>
        </div>
    `;
}

/* ======================
   EVENT BINDINGS
====================== */

DOM.form.addEventListener("submit", e => {
    e.preventDefault();
    startRun();
});

DOM.closeBtn.addEventListener("click", cancelRun);

attachAutocomplete("start-input", "start-suggestions");
attachAutocomplete("end-input", "end-suggestions");

if (history.replaceState) {
    // Prevent form resubmission on reload/back navigation
    history.replaceState(null, null, location.href);
}
