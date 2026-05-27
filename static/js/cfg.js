/*
cfg.js

Frontend for the CFG -> PDA page.

What it does:
- Sends the CFG to /api/cfg/pda, renders the PDA in Cytoscape.
- Sends a test string to /api/cfg/check, animates the step trace:
    * the active state lights up (sticky) and pulses on entry,
    * the transition edge between consecutive states gets "marching ants"
      (animated line-dash-offset) so the direction of travel is obvious,
    * the stack panel updates per step with push/pop flashes on the top box.
*/

const cfgInput     = document.getElementById('cfg-input');
const cfgConvertBtn = document.getElementById('cfg-convert-btn');
const cfgRunBtn    = document.getElementById('cfg-run-btn');
const cfgResetBtn  = document.getElementById('cfg-reset-btn');
const cfgStepsList = document.getElementById('cfg-steps-list');
const stackContents = document.getElementById('stack-contents');
const cfgMultiStringRows = document.querySelectorAll('#cfg-multi-checker .multi-string-row');

let cyPda = null;
let currentPda = null;
let currentSteps = null;
let lastStack = [];

async function postJson(url, body) {
    const res = await fetch(url, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(body),
    });
    return res.json();
}
function sleep(ms) { return new Promise(r => setTimeout(r, ms)); }

function clearCfgSteps() { cfgStepsList.innerHTML = ''; }
function addCfgStep(text) {
    const li = document.createElement('li');
    li.textContent = text;
    cfgStepsList.appendChild(li);
    // Keep the newest step visible inside the scrollable step viewer.
    cfgStepsList.scrollTop = cfgStepsList.scrollHeight;
}

function setCfgStringResult(row, valid, value, error) {
    const result = row.querySelector('.string-result');
    result.classList.remove('pending', 'accepted', 'rejected');
    if (error) {
        result.classList.add('rejected');
        result.textContent = 'Error';
        return;
    }
    result.classList.add(valid ? 'accepted' : 'rejected');
    if (value === '') {
        result.textContent = valid ? 'Null String Accepted' : 'Null String Not Accepted';
    } else {
        result.textContent = valid ? 'String Accepted' : 'String Not Accepted';
    }
}

function resetCfgStringResults() {
    cfgMultiStringRows.forEach(row => {
        const result = row.querySelector('.string-result');
        result.classList.remove('accepted', 'rejected');
        result.classList.add('pending');
        result.textContent = 'Not Checked';
    });
}

async function checkCfgStringRow(row) {
    if (!currentPda) return;
    const input = row.querySelector('.multi-string-input');
    const value = input.value || '';
    const res = await postJson('/api/cfg/check', { pda: currentPda, string: value });
    setCfgStringResult(row, !!res.valid, value, res.error);
}

async function checkAllCfgStrings() {
    if (!currentPda) return;
    await Promise.all(Array.from(cfgMultiStringRows).map(checkCfgStringRow));
}

// ----------------------------- Marching ants ----------------------------- //

let antsTimer = null;
let antsOffset = 0;
function startAnts() {
    if (antsTimer) return;
    antsTimer = setInterval(() => {
        antsOffset = (antsOffset - 3) % 1000;
        if (!cyPda) return;
        cyPda.edges('.traversing').forEach(e => e.style('line-dash-offset', antsOffset));
    }, 60);
}
function stopAnts() {
    if (antsTimer) { clearInterval(antsTimer); antsTimer = null; }
}

// ----------------------------- Cytoscape build ----------------------------- //

function buildPdaElements(pda) {
    const nodes = pda.states.map(s => ({ data: { id: s, label: s } }));
    const edges = [];
    let edgeId = 0;
    for (const t of pda.transitions) {
        const pushStr = (t.push && t.push.length) ? t.push.join('') : 'ε';
        const label = `${t.input || 'ε'}, ${t.stack_top} → ${pushStr}`;
        edges.push({
            data: {
                id: 'pe' + (edgeId++),
                source: t.from,
                target: t.to,
                label,
                input: t.input,
                stack_top: t.stack_top,
                push: (t.push || []).join(','),
            },
        });
    }
    return { nodes, edges };
}

function createCy(containerId, elements) {
    // Prefer dagre (loaded via the cytoscape-dagre CDN in cfg.html); fall back
    // to cose if it didn't load for any reason.
    const layout = (typeof cytoscape.use === 'function')
        ? { name: 'dagre', rankDir: 'LR', nodeSep: 30, rankSep: 60, animate: false }
        : { name: 'cose', animate: true };
    return cytoscape({
        container: document.getElementById(containerId),
        elements: elements.nodes.concat(elements.edges),
        style: [
            { selector: 'node', style: {
                'label': 'data(label)',
                'text-valign': 'center',
                'text-halign': 'center',
                'background-color': '#fff',
                'border-color': '#333',
                'border-width': 2,
                'width': 46, 'height': 46,
                'transition-property': 'background-color, border-color, border-width, width, height',
                'transition-duration': 180,
            }},
            { selector: 'edge', style: {
                'label': 'data(label)',
                'curve-style': 'bezier',
                'target-arrow-shape': 'triangle',
                'line-color': '#888',
                'target-arrow-color': '#888',
                'text-rotation': 'autorotate',
                'font-size': 10,
                'transition-property': 'line-color, target-arrow-color, width',
                'transition-duration': 150,
            }},
            { selector: '.active', style: {
                'background-color': '#ffe082',
                'border-color': '#ffb300',
                'border-width': 4,
            }},
            { selector: '.accept', style: {
                'border-width': 6,
                'border-style': 'double',
            }},
            { selector: '.pulse', style: {
                'width': 56, 'height': 56,
                'border-color': '#ff9800',
                'border-width': 6,
            }},
            { selector: 'edge.traversing', style: {
                'line-color': '#ff9800',
                'target-arrow-color': '#ff9800',
                'line-style': 'dashed',
                'line-dash-pattern': [8, 4],
                'width': 4,
            }},
            { selector: '.valid', style: {
                'background-color': '#2e7d32', 'border-color': '#2e7d32',
                'line-color': '#2e7d32',     'target-arrow-color': '#2e7d32',
            }},
            { selector: '.invalid', style: {
                'background-color': '#c62828', 'border-color': '#c62828',
                'line-color': '#c62828',     'target-arrow-color': '#c62828',
            }},
        ],
        layout: layout,
    });
}

function pulseNode(node) {
    if (!node) return;
    node.addClass('pulse');
    setTimeout(() => node.removeClass('pulse'), 280);
}

/** Edges are built in the same order as `pda.transitions` (id "pe" + index),
 *  so we can look up the exact edge by the simulator's `applied_idx` — no
 *  more guessing among the many self-loops on q1. */
function edgeForTransition(cy, idx) {
    if (idx === null || idx === undefined) return cy.collection();
    return cy.getElementById('pe' + idx);
}

// ----------------------------- Stack rendering ----------------------------- //

/** Re-render the stack panel and flash any boxes that were just pushed or
 *  popped relative to the previous frame. */
function renderStack(stack) {
    stack = stack || [];
    if (stack.length === 0) {
        stackContents.innerHTML = 'Empty Stack';
        lastStack = [];
        return;
    }
    stackContents.innerHTML = '';
    const reversed = stack.slice().reverse(); // top first visually
    reversed.forEach((sym, idx) => {
        const div = document.createElement('div');
        div.className = 'stack-box';
        if (idx === 0) div.classList.add('stack-top');
        div.textContent = sym;
        stackContents.appendChild(div);
    });

    // Flash the new top if it differs from the previous top.
    const prevTop = lastStack.length ? lastStack[lastStack.length - 1] : null;
    const newTop  = stack[stack.length - 1];
    if (newTop !== prevTop) {
        const topBox = stackContents.firstChild;
        if (topBox) {
            topBox.classList.add(stack.length > lastStack.length ? 'push' : 'pop');
            setTimeout(() => topBox.classList.remove('push', 'pop'), 500);
        }
    }
    lastStack = stack.slice();
}

// ----------------------------- Convert ----------------------------- //

cfgConvertBtn.addEventListener('click', async () => {
    const cfgText = cfgInput.value.trim();
    if (!cfgText) { alert('Please enter CFG rules.'); return; }

    clearCfgSteps();
    addCfgStep('Parsing CFG and constructing PDA...');

    const pdaResp = await postJson('/api/cfg/pda', { cfg: cfgText });
    if (pdaResp.error) { addCfgStep('Error: ' + pdaResp.error); return; }
    currentPda = pdaResp;
    addCfgStep('PDA constructed.');

    const els = buildPdaElements(currentPda);
    if (cyPda) cyPda.destroy();
    cyPda = createCy('cy-pda', els);
    (currentPda.accept_states || []).forEach(s => {
        const node = cyPda.getElementById(s);
        if (node) node.addClass('accept');
    });

    addCfgStep('PDA diagram rendered.');
    await checkAllCfgStrings();
});

// ----------------------------- Run (animate) ----------------------------- //

cfgRunBtn.addEventListener('click', async () => {
    if (!currentPda) { alert('Please convert CFG first.'); return; }
    const s = document.getElementById('cfg-test-input').value || '';
    await runPda(s);
});

async function runPda(s) {
    clearCfgSteps();
    addCfgStep('Requesting PDA simulation...');

    const res = await postJson('/api/cfg/check', { pda: currentPda, string: s });
    if (res.error) { addCfgStep('Error: ' + res.error); return; }

    currentSteps = res.steps || [];
    const valid = !!res.valid;

    cyPda.elements().removeClass('active traversing valid invalid pulse');
    lastStack = [];
    startAnts();

    const delay = 700;
    let currentActiveId = null;

    for (let i = 0; i < currentSteps.length; i++) {
        const step = currentSteps[i];

        // Edge highlight: clear previous, then light up exactly the edge the
        // simulator says fired (no guessing among self-loops on q1).
        cyPda.edges('.traversing').removeClass('traversing');
        edgeForTransition(cyPda, step.applied_idx).addClass('traversing');

        // State highlight: only toggle .active when the state actually changes
        // so we don't get a flicker (white -> yellow) on every q1->q1 step.
        // Always pulse so the user still sees that "something happened."
        if (step.state !== currentActiveId) {
            if (currentActiveId) cyPda.getElementById(currentActiveId).removeClass('active');
            const node = cyPda.getElementById(step.state);
            if (node) node.addClass('active');
            currentActiveId = step.state;
        }
        const activeNode = cyPda.getElementById(step.state);
        if (activeNode) pulseNode(activeNode);

        // Stack panel + step line.
        renderStack(step.stack);
        addCfgStep(`State: ${step.state}, remaining: "${step.remaining_input}", stack: [${(step.stack || []).join(',')}]`);

        await sleep(delay);
    }

    cyPda.edges('.traversing').removeClass('traversing');
    stopAnts();

    if (cyPda) {
        if (valid) cyPda.elements().addClass('valid');
        else cyPda.elements().addClass('invalid');
    }
    if (res.error) addCfgStep('Warning: ' + res.error);
    addCfgStep(valid ? 'Result: VALID (string accepted)' : 'Result: INVALID (string rejected)');
}

cfgMultiStringRows.forEach(row => {
    const input = row.querySelector('.multi-string-input');
    const simulateBtn = row.querySelector('.simulate-string-btn');
    input.addEventListener('input', () => checkCfgStringRow(row));
    simulateBtn.addEventListener('click', async () => {
        if (!currentPda) { alert('Please convert CFG first.'); return; }
        document.getElementById('cfg-test-input').value = input.value || '';
        await checkCfgStringRow(row);
        await runPda(input.value || '');
    });
});

// ----------------------------- Reset ----------------------------- //

cfgResetBtn.addEventListener('click', () => {
    stopAnts();
    if (cyPda) cyPda.elements().removeClass('active traversing valid invalid pulse');
    stackContents.innerHTML = 'Empty Stack';
    lastStack = [];
    resetCfgStringResults();
    clearCfgSteps();
    addCfgStep('Reset complete.');
});

// Initial state
clearCfgSteps();
addCfgStep('Ready. Enter CFG rules and click Convert.');
